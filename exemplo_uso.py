#!/usr/bin/env python3
"""
Exemplo de uso do Organizador de Imagens
Cria um diretório de teste com imagens duplicadas e executa o organizador
"""

import os
import shutil
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def criar_diretorio_teste():
    """Cria um diretório temporário com imagens de exemplo."""
    temp_dir = tempfile.mkdtemp(prefix="exemplo_imagens_")
    test_dir = Path(temp_dir)
    
    print(f"Criando diretório de teste em: {test_dir}")
    
    # Criar imagem 1 (única)
    img1 = Image.new('RGB', (200, 200), color=(135, 206, 235))  # Sky blue
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([50, 50, 150, 150], fill=(255, 215, 0))  # Gold square
    img1.save(test_dir / "paisagem_1.jpg", quality=95)
    print("Criada: paisagem_1.jpg (única)")
    
    # Criar imagem 2 (única)
    img2 = Image.new('RGB', (200, 200), color=(34, 139, 34))  # Forest green
    draw2 = ImageDraw.Draw(img2)
    draw2.ellipse([50, 50, 150, 150], fill=(255, 0, 0))  # Red circle
    img2.save(test_dir / "paisagem_2.jpg", quality=95)
    print("Criada: paisagem_2.jpg (única)")
    
    # Criar imagem 3 (original)
    img3 = Image.new('RGB', (200, 200), color=(70, 130, 180))  # Steel blue
    draw3 = ImageDraw.Draw(img3)
    draw3.polygon([(100, 50), (150, 150), (50, 150)], fill=(255, 255, 0))  # Yellow triangle
    img3.save(test_dir / "montanha_original.jpg", quality=95)
    print("Criada: montanha_original.jpg")
    
    # Criar cópia exata da imagem 3
    shutil.copy2(test_dir / "montanha_original.jpg", test_dir / "montanha_copia_1.jpg")
    print("Criada: montanha_copia_1.jpg (cópia exata)")
    
    # Criar outra cópia exata da imagem 3
    shutil.copy2(test_dir / "montanha_original.jpg", test_dir / "montanha_copia_2.jpg")
    print("Criada: montanha_copia_2.jpg (cópia exata)")
    
    # Criar imagem 4 (original)
    img4 = Image.new('RGB', (200, 200), color=(240, 128, 128))  # Light coral
    draw4 = ImageDraw.Draw(img4)
    draw4.rectangle([30, 30, 170, 170], outline=(0, 0, 0), width=5)
    img4.save(test_dir / "retrato_original.png", quality=95)
    print("Criada: retrato_original.png")
    
    # Criar versão com metadados diferentes (visualmente similar)
    # Salvar em formato diferente e qualidade diferente
    img4.save(test_dir / "retrato_editado.jpg", quality=85)
    print("Criada: retrato_editado.jpg (visualmente similar)")
    
    # Criar imagem 5 (única)
    img5 = Image.new('RGB', (200, 200), color=(255, 192, 203))  # Pink
    draw5 = ImageDraw.Draw(img5)
    for i in range(0, 200, 20):
        draw5.line([(i, 0), (i, 200)], fill=(255, 255, 255), width=2)
        draw5.line([(0, i), (200, i)], fill=(255, 255, 255), width=2)
    img5.save(test_dir / "grade.jpg", quality=95)
    print("Criada: grade.jpg (única)")
    
    print(f"\nTotal de imagens criadas: 8")
    print(f"  - Únicas: 3 (paisagem_1, paisagem_2, grade)")
    print(f"  - Duplicatas exatas: 3 (montanha_original + 2 cópias)")
    print(f"  - Duplicatas visuais: 2 (retrato em PNG e JPG)")
    
    return test_dir

def main():
    """Função principal do exemplo."""
    print("=" * 70)
    print("EXEMPLO DE USO DO ORGANIZADOR DE IMAGENS")
    print("=" * 70)
    print()
    
    # Criar diretório de teste
    test_dir = criar_diretorio_teste()
    
    print("\n" + "=" * 70)
    print("EXECUTANDO ORGANIZADOR")
    print("=" * 70)
    print()
    
    # Importar e executar o organizador
    from organizador_imagens import OrganizadorImagens
    
    organizador = OrganizadorImagens(test_dir)
    organizador.processar()
    
    print("\n" + "=" * 70)
    print("RESULTADO")
    print("=" * 70)
    print(f"\nOs arquivos foram organizados em:")
    print(f"  - Validadas: {test_dir / 'validadas'}")
    print(f"  - Repetidas: {test_dir / 'repetidas'}")
    print(f"\nLog salvo em: {test_dir.parent / 'organizador_imagens.log'}")
    print(f"\nDiretório de teste: {test_dir}")
    print("\nVocê pode explorar os diretórios para verificar os resultados.")
    print("Quando terminar, você pode deletar o diretório temporário.")

if __name__ == "__main__":
    main()
