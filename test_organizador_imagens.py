#!/usr/bin/env python3
"""
Testes para o Organizador de Imagens em Duplicidade
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import hashlib

# Adicionar o diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from organizador_imagens import OrganizadorImagens, SUPPORTED_FORMATS


class TestOrganizadorImagens(unittest.TestCase):
    """Testes para a classe OrganizadorImagens."""
    
    def setUp(self):
        """Configuração antes de cada teste."""
        # Criar diretório temporário para testes
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
    def tearDown(self):
        """Limpeza após cada teste."""
        # Remover diretório temporário
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _criar_imagem_teste(self, nome: str, tamanho=(100, 100), cor=(255, 0, 0)):
        """
        Cria uma imagem de teste.
        
        Args:
            nome: Nome do arquivo
            tamanho: Tupla (largura, altura)
            cor: Tupla RGB
            
        Returns:
            Path do arquivo criado
        """
        caminho = self.test_dir / nome
        img = Image.new('RGB', tamanho, color=cor)
        img.save(caminho)
        return caminho
    
    def test_inicializacao(self):
        """Testa a inicialização do organizador."""
        org = OrganizadorImagens(self.test_dir)
        self.assertEqual(org.diretorio_origem, self.test_dir)
        self.assertEqual(org.diretorio_validadas, self.test_dir / 'validadas')
        self.assertEqual(org.diretorio_repetidas, self.test_dir / 'repetidas')
        self.assertEqual(org.total_imagens, 0)
        self.assertEqual(org.imagens_validadas, 0)
        self.assertEqual(org.imagens_repetidas, 0)
    
    def test_eh_imagem_suportada(self):
        """Testa a verificação de formatos suportados."""
        org = OrganizadorImagens(self.test_dir)
        
        # Formatos suportados
        for ext in SUPPORTED_FORMATS:
            self.assertTrue(org._eh_imagem_suportada(Path(f"teste{ext}")))
            self.assertTrue(org._eh_imagem_suportada(Path(f"teste{ext.upper()}")))
        
        # Formatos não suportados
        self.assertFalse(org._eh_imagem_suportada(Path("teste.txt")))
        self.assertFalse(org._eh_imagem_suportada(Path("teste.pdf")))
        self.assertFalse(org._eh_imagem_suportada(Path("teste.docx")))
    
    def test_calcular_md5(self):
        """Testa o cálculo de hash MD5."""
        # Criar imagem de teste
        img_path = self._criar_imagem_teste("test.jpg")
        
        org = OrganizadorImagens(self.test_dir)
        hash1 = org._calcular_md5(img_path)
        
        # Verificar que o hash foi gerado
        self.assertTrue(hash1)
        self.assertEqual(len(hash1), 32)  # MD5 tem 32 caracteres hexadecimais
        
        # Verificar que o mesmo arquivo gera o mesmo hash
        hash2 = org._calcular_md5(img_path)
        self.assertEqual(hash1, hash2)
    
    def test_calcular_phash(self):
        """Testa o cálculo de hash perceptual."""
        # Criar imagem de teste
        img_path = self._criar_imagem_teste("test.png")
        
        org = OrganizadorImagens(self.test_dir)
        phash = org._calcular_phash(img_path)
        
        # Verificar que o hash foi gerado
        self.assertTrue(phash)
        self.assertTrue(len(phash) > 0)
    
    def test_coletar_imagens(self):
        """Testa a coleta de imagens do diretório."""
        # Criar algumas imagens de teste
        self._criar_imagem_teste("img1.jpg")
        self._criar_imagem_teste("img2.png")
        self._criar_imagem_teste("img3.gif")
        
        # Criar um arquivo não-imagem
        (self.test_dir / "texto.txt").write_text("teste")
        
        org = OrganizadorImagens(self.test_dir)
        imagens = org._coletar_imagens()
        
        # Verificar que apenas imagens foram coletadas
        self.assertEqual(len(imagens), 3)
        self.assertEqual(org.total_imagens, 3)
    
    def test_criar_diretorios(self):
        """Testa a criação dos diretórios de destino."""
        org = OrganizadorImagens(self.test_dir)
        org._criar_diretorios()
        
        # Verificar que os diretórios foram criados
        self.assertTrue(org.diretorio_validadas.exists())
        self.assertTrue(org.diretorio_validadas.is_dir())
        self.assertTrue(org.diretorio_repetidas.exists())
        self.assertTrue(org.diretorio_repetidas.is_dir())
    
    def test_duplicatas_exatas(self):
        """Testa a detecção de duplicatas exatas (MD5)."""
        # Criar imagem original
        img1_path = self._criar_imagem_teste("img1.jpg", cor=(255, 0, 0))
        
        # Criar cópia exata
        img2_path = self.test_dir / "img2.jpg"
        shutil.copy2(img1_path, img2_path)
        
        # Criar imagem diferente
        img3_path = self._criar_imagem_teste("img3.jpg", cor=(0, 255, 0))
        
        # Processar
        org = OrganizadorImagens(self.test_dir)
        org.processar()
        
        # Verificar resultados
        # Deve ter 1 imagem validada (img3) e 2 repetidas (img1, img2)
        self.assertEqual(org.imagens_validadas, 1)
        self.assertEqual(org.imagens_repetidas, 2)
        
        # Verificar que os diretórios foram criados
        self.assertTrue(org.diretorio_validadas.exists())
        self.assertTrue(org.diretorio_repetidas.exists())
        
        # Verificar que há um grupo de duplicatas
        grupos = [d for d in org.diretorio_repetidas.iterdir() if d.is_dir()]
        self.assertEqual(len(grupos), 1)
        
        # Verificar que o grupo contém 2 imagens
        imagens_no_grupo = list(grupos[0].glob("*.jpg"))
        self.assertEqual(len(imagens_no_grupo), 2)
    
    def test_imagens_unicas(self):
        """Testa o processamento de imagens únicas."""
        # Criar 3 imagens diferentes com padrões distintos
        # Usar tamanhos diferentes e padrões para garantir hashes perceptuais diferentes
        img1 = Image.new('RGB', (100, 100), color=(255, 0, 0))
        # Adicionar um padrão para diferenciar
        for i in range(0, 100, 10):
            for j in range(100):
                img1.putpixel((i, j), (0, 0, 0))
        img1.save(self.test_dir / "img1.jpg")
        
        img2 = Image.new('RGB', (100, 100), color=(0, 255, 0))
        # Padrão diferente
        for i in range(100):
            for j in range(0, 100, 10):
                img2.putpixel((i, j), (0, 0, 0))
        img2.save(self.test_dir / "img2.jpg")
        
        img3 = Image.new('RGB', (100, 100), color=(0, 0, 255))
        # Padrão diagonal
        for i in range(100):
            img3.putpixel((i, i), (255, 255, 255))
        img3.save(self.test_dir / "img3.jpg")
        
        # Processar
        org = OrganizadorImagens(self.test_dir)
        org.processar()
        
        # Verificar que todas as 3 imagens são únicas
        self.assertEqual(org.imagens_validadas, 3)
        self.assertEqual(org.imagens_repetidas, 0)
        
        # Verificar que as imagens estão na pasta validadas
        imagens_validadas = list(org.diretorio_validadas.glob("*.jpg"))
        self.assertEqual(len(imagens_validadas), 3)
    
    def test_preservacao_metadata(self):
        """Testa se os metadados são preservados com shutil.copy2."""
        # Criar imagem de teste
        img_path = self._criar_imagem_teste("test.jpg")
        
        # Modificar o tempo de modificação
        import time
        timestamp = time.time() - 86400  # 1 dia atrás
        os.utime(img_path, (timestamp, timestamp))
        mtime_original = os.path.getmtime(img_path)
        
        # Processar
        org = OrganizadorImagens(self.test_dir)
        org.processar()
        
        # Verificar que a imagem foi copiada para validadas
        imagem_copiada = list(org.diretorio_validadas.glob("*.jpg"))[0]
        mtime_copiada = os.path.getmtime(imagem_copiada)
        
        # Verificar que o tempo de modificação foi preservado (com tolerância de 1 segundo)
        self.assertAlmostEqual(mtime_original, mtime_copiada, delta=1.0)
    
    def test_formatos_multiplos(self):
        """Testa o suporte a múltiplos formatos de imagem."""
        # Criar imagens em diferentes formatos
        self._criar_imagem_teste("img1.jpg")
        self._criar_imagem_teste("img2.png")
        self._criar_imagem_teste("img3.gif")
        self._criar_imagem_teste("img4.bmp")
        self._criar_imagem_teste("img5.webp")
        
        # Processar
        org = OrganizadorImagens(self.test_dir)
        imagens = org._coletar_imagens()
        
        # Verificar que todas as imagens foram coletadas
        self.assertEqual(len(imagens), 5)
    
    def test_diretorio_vazio(self):
        """Testa o comportamento com diretório vazio."""
        org = OrganizadorImagens(self.test_dir)
        org.processar()
        
        # Verificar que nenhuma imagem foi processada
        self.assertEqual(org.total_imagens, 0)
        self.assertEqual(org.imagens_validadas, 0)
        self.assertEqual(org.imagens_repetidas, 0)
    
    def test_ignorar_diretorios_destino(self):
        """Testa que os diretórios de destino são ignorados na coleta."""
        # Criar imagem no diretório principal
        self._criar_imagem_teste("img1.jpg")
        
        # Criar diretórios de destino com imagens
        validadas_dir = self.test_dir / 'validadas'
        validadas_dir.mkdir()
        img_validadas = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img_validadas.save(validadas_dir / "img_validada.jpg")
        
        repetidas_dir = self.test_dir / 'repetidas'
        repetidas_dir.mkdir()
        img_repetidas = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img_repetidas.save(repetidas_dir / "img_repetida.jpg")
        
        # Processar
        org = OrganizadorImagens(self.test_dir)
        imagens = org._coletar_imagens()
        
        # Verificar que apenas a imagem do diretório principal foi coletada
        self.assertEqual(len(imagens), 1)


class TestIntegracao(unittest.TestCase):
    """Testes de integração."""
    
    def setUp(self):
        """Configuração antes de cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_fluxo_completo(self):
        """Testa o fluxo completo de organização."""
        # Criar cenário de teste:
        # - 2 imagens idênticas (duplicatas exatas)
        # - 1 imagem única
        
        # Imagem 1
        img1 = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img1_path = self.test_dir / "red1.jpg"
        img1.save(img1_path)
        
        # Imagem 2 (cópia de img1)
        img2_path = self.test_dir / "red2.jpg"
        shutil.copy2(img1_path, img2_path)
        
        # Imagem 3 (única)
        img3 = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img3_path = self.test_dir / "green.jpg"
        img3.save(img3_path)
        
        # Processar
        org = OrganizadorImagens(self.test_dir)
        org.processar()
        
        # Verificar estrutura de diretórios
        self.assertTrue((self.test_dir / 'validadas').exists())
        self.assertTrue((self.test_dir / 'repetidas').exists())
        
        # Verificar estatísticas
        self.assertEqual(org.total_imagens, 3)
        self.assertEqual(org.imagens_validadas, 1)
        self.assertEqual(org.imagens_repetidas, 2)
        
        # Verificar conteúdo dos diretórios
        validadas = list((self.test_dir / 'validadas').glob('*.jpg'))
        self.assertEqual(len(validadas), 1)
        
        # Verificar grupos de repetidas
        grupos = [d for d in (self.test_dir / 'repetidas').iterdir() if d.is_dir()]
        self.assertEqual(len(grupos), 1)
        
        # Verificar que o grupo contém 2 imagens
        repetidas = list(grupos[0].glob('*.jpg'))
        self.assertEqual(len(repetidas), 2)
        
        # Verificar que os arquivos originais ainda existem
        self.assertTrue(img1_path.exists())
        self.assertTrue(img2_path.exists())
        self.assertTrue(img3_path.exists())


def run_tests():
    """Executa todos os testes."""
    # Criar suite de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TestOrganizadorImagens))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegracao))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar código de saída
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
