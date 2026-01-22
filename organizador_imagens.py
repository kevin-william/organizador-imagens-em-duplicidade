#!/usr/bin/env python3
"""
Organizador de Imagens em Duplicidade
Organiza imagens duplicadas usando hash duplo: MD5 para cópias exatas e 
hash perceptual para imagens visualmente idênticas.
"""

import os
import sys
import hashlib
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from PIL import Image
import imagehash

# Formatos de imagem suportados
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organizador_imagens.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OrganizadorImagens:
    """Classe principal para organizar imagens duplicadas."""
    
    def __init__(self, diretorio_origem: str):
        """
        Inicializa o organizador de imagens.
        
        Args:
            diretorio_origem: Caminho do diretório contendo as imagens
        """
        self.diretorio_origem = Path(diretorio_origem)
        self.diretorio_validadas = self.diretorio_origem / 'validadas'
        self.diretorio_repetidas = self.diretorio_origem / 'repetidas'
        
        # Dicionários para armazenar hashes
        self.md5_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.phashes: Dict[str, List[Path]] = defaultdict(list)
        
        # Estatísticas
        self.total_imagens = 0
        self.imagens_validadas = 0
        self.imagens_repetidas = 0
        
    def _criar_diretorios(self):
        """Cria os diretórios de destino se não existirem."""
        self.diretorio_validadas.mkdir(exist_ok=True)
        self.diretorio_repetidas.mkdir(exist_ok=True)
        logger.info(f"Diretórios criados: {self.diretorio_validadas}, {self.diretorio_repetidas}")
    
    def _eh_imagem_suportada(self, arquivo: Path) -> bool:
        """
        Verifica se o arquivo é uma imagem suportada.
        
        Args:
            arquivo: Caminho do arquivo
            
        Returns:
            True se for uma imagem suportada, False caso contrário
        """
        return arquivo.suffix.lower() in SUPPORTED_FORMATS
    
    def _calcular_md5(self, arquivo: Path) -> str:
        """
        Calcula o hash MD5 de um arquivo.
        
        Args:
            arquivo: Caminho do arquivo
            
        Returns:
            String hexadecimal do hash MD5
        """
        md5 = hashlib.md5()
        try:
            with open(arquivo, 'rb') as f:
                # Ler em blocos para eficiência com arquivos grandes
                for chunk in iter(lambda: f.read(8192), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular MD5 de {arquivo}: {e}")
            return ""
    
    def _calcular_phash(self, arquivo: Path) -> str:
        """
        Calcula o hash perceptual de uma imagem.
        
        Args:
            arquivo: Caminho do arquivo de imagem
            
        Returns:
            String do hash perceptual
        """
        try:
            with Image.open(arquivo) as img:
                # Usar phash (perceptual hash) para detectar imagens visualmente similares
                phash = imagehash.phash(img)
                return str(phash)
        except Exception as e:
            logger.error(f"Erro ao calcular hash perceptual de {arquivo}: {e}")
            return ""
    
    def _coletar_imagens(self) -> List[Path]:
        """
        Coleta todas as imagens do diretório de origem.
        
        Returns:
            Lista de caminhos de arquivos de imagem
        """
        imagens = []
        logger.info(f"Coletando imagens de {self.diretorio_origem}")
        
        for arquivo in self.diretorio_origem.iterdir():
            # Ignorar diretórios de destino
            if arquivo.is_dir() and arquivo.name in ['validadas', 'repetidas']:
                continue
            
            if arquivo.is_file() and self._eh_imagem_suportada(arquivo):
                imagens.append(arquivo)
        
        self.total_imagens = len(imagens)
        logger.info(f"Total de imagens encontradas: {self.total_imagens}")
        return imagens
    
    def _processar_hashes(self, imagens: List[Path]):
        """
        Processa e armazena os hashes de todas as imagens.
        
        Args:
            imagens: Lista de caminhos de arquivos de imagem
        """
        logger.info("Calculando hashes...")
        
        for i, arquivo in enumerate(imagens, 1):
            if i % 100 == 0:
                logger.info(f"Processado {i}/{self.total_imagens} imagens")
            
            # Calcular MD5 (para duplicatas exatas)
            md5_hash = self._calcular_md5(arquivo)
            if md5_hash:
                self.md5_hashes[md5_hash].append(arquivo)
            
            # Calcular hash perceptual (para duplicatas visuais)
            phash = self._calcular_phash(arquivo)
            if phash:
                self.phashes[phash].append(arquivo)
        
        logger.info("Cálculo de hashes concluído")
    
    def _organizar_imagens(self):
        """
        Organiza as imagens em diretórios de validadas e repetidas.
        """
        logger.info("Organizando imagens...")
        
        # Conjunto de arquivos já processados
        processados: Set[Path] = set()
        
        # Primeiro, processar duplicatas exatas (MD5)
        grupo_id = 1
        for md5_hash, arquivos in self.md5_hashes.items():
            if len(arquivos) > 1:
                # Duplicatas exatas encontradas
                logger.info(f"Grupo {grupo_id}: {len(arquivos)} duplicatas exatas (MD5)")
                
                # Criar subpasta para este grupo
                grupo_dir = self.diretorio_repetidas / f"grupo_{grupo_id:04d}_md5"
                grupo_dir.mkdir(exist_ok=True)
                
                # Copiar todas as duplicatas para a pasta do grupo
                for arquivo in arquivos:
                    destino = grupo_dir / arquivo.name
                    # Se houver conflito de nome, adicionar sufixo
                    contador = 1
                    while destino.exists():
                        destino = grupo_dir / f"{arquivo.stem}_{contador}{arquivo.suffix}"
                        contador += 1
                    
                    shutil.copy2(arquivo, destino)
                    processados.add(arquivo)
                    self.imagens_repetidas += 1
                
                grupo_id += 1
        
        # Segundo, processar duplicatas visuais (phash) que não são duplicatas exatas
        for phash, arquivos in self.phashes.items():
            if len(arquivos) > 1:
                # Verificar se não são duplicatas exatas (já processadas)
                arquivos_nao_processados = [a for a in arquivos if a not in processados]
                
                if len(arquivos_nao_processados) > 1:
                    # Duplicatas visuais encontradas
                    logger.info(f"Grupo {grupo_id}: {len(arquivos_nao_processados)} duplicatas visuais (phash)")
                    
                    # Criar subpasta para este grupo
                    grupo_dir = self.diretorio_repetidas / f"grupo_{grupo_id:04d}_phash"
                    grupo_dir.mkdir(exist_ok=True)
                    
                    # Copiar todas as duplicatas para a pasta do grupo
                    for arquivo in arquivos_nao_processados:
                        destino = grupo_dir / arquivo.name
                        # Se houver conflito de nome, adicionar sufixo
                        contador = 1
                        while destino.exists():
                            destino = grupo_dir / f"{arquivo.stem}_{contador}{arquivo.suffix}"
                            contador += 1
                        
                        shutil.copy2(arquivo, destino)
                        processados.add(arquivo)
                        self.imagens_repetidas += 1
                    
                    grupo_id += 1
        
        # Copiar imagens únicas para a pasta validadas
        for md5_hash, arquivos in self.md5_hashes.items():
            if len(arquivos) == 1:
                arquivo = arquivos[0]
                # Verificar se não foi processado como duplicata visual
                if arquivo not in processados:
                    destino = self.diretorio_validadas / arquivo.name
                    # Se houver conflito de nome, adicionar sufixo
                    contador = 1
                    while destino.exists():
                        destino = self.diretorio_validadas / f"{arquivo.stem}_{contador}{arquivo.suffix}"
                        contador += 1
                    
                    shutil.copy2(arquivo, destino)
                    self.imagens_validadas += 1
        
        logger.info("Organização concluída")
    
    def _imprimir_estatisticas(self):
        """Imprime as estatísticas do processamento."""
        logger.info("=" * 60)
        logger.info("ESTATÍSTICAS")
        logger.info("=" * 60)
        logger.info(f"Total de imagens processadas: {self.total_imagens}")
        logger.info(f"Imagens únicas (validadas): {self.imagens_validadas}")
        logger.info(f"Imagens duplicadas (repetidas): {self.imagens_repetidas}")
        logger.info(f"Grupos de duplicatas: {len([d for d in self.diretorio_repetidas.iterdir() if d.is_dir()])}")
        logger.info("=" * 60)
    
    def processar(self):
        """
        Executa o processo completo de organização de imagens.
        """
        logger.info("Iniciando organização de imagens")
        
        # Verificar se o diretório existe
        if not self.diretorio_origem.exists():
            logger.error(f"Diretório não encontrado: {self.diretorio_origem}")
            return
        
        # Criar diretórios de destino
        self._criar_diretorios()
        
        # Coletar imagens
        imagens = self._coletar_imagens()
        
        if not imagens:
            logger.warning("Nenhuma imagem encontrada")
            return
        
        # Processar hashes
        self._processar_hashes(imagens)
        
        # Organizar imagens
        self._organizar_imagens()
        
        # Imprimir estatísticas
        self._imprimir_estatisticas()
        
        logger.info("Processamento concluído com sucesso")


def main():
    """Função principal."""
    if len(sys.argv) != 2:
        print("Uso: python organizador_imagens.py <diretorio>")
        print("Exemplo: python organizador_imagens.py /caminho/para/imagens")
        sys.exit(1)
    
    diretorio = sys.argv[1]
    
    organizador = OrganizadorImagens(diretorio)
    organizador.processar()


if __name__ == "__main__":
    main()
