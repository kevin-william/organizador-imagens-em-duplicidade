# Organizador de Imagens em Duplicidade

Um script Python eficiente para identificar e organizar imagens duplicadas usando hash duplo: MD5 para cópias exatas e hash perceptual (imagehash) para imagens visualmente idênticas.

## Características

- ✅ **Detecção de Duplicatas Exatas**: Usa hash MD5 para identificar cópias byte-a-byte idênticas
- ✅ **Detecção de Duplicatas Visuais**: Usa hash perceptual para identificar imagens visualmente similares mesmo com metadados diferentes
- ✅ **Múltiplos Formatos**: Suporta JPG, JPEG, PNG, GIF, BMP, WEBP
- ✅ **Preservação de Originais**: Usa `shutil.copy2` para manter os arquivos originais intactos
- ✅ **Organização Inteligente**: 
  - Pasta `validadas`: Imagens únicas
  - Pasta `repetidas`: Grupos de duplicatas organizados em subpastas
- ✅ **Eficiente**: Otimizado para processar milhares de imagens
- ✅ **Logs Detalhados**: Registro completo do processamento
- ✅ **Testado**: Suite completa de testes unitários e de integração

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/kevin-william/organizador-imagens-em-duplicidade.git
cd organizador-imagens-em-duplicidade
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Uso Básico

Execute o script passando o diretório contendo as imagens:

```bash
python organizador_imagens.py /caminho/para/suas/imagens
```

### Exemplo

```bash
python organizador_imagens.py ~/Downloads/fotos
```

### Estrutura de Saída

Após a execução, a estrutura de diretórios será:

```
/caminho/para/suas/imagens/
├── validadas/              # Imagens únicas
│   ├── foto1.jpg
│   ├── foto2.png
│   └── ...
├── repetidas/              # Imagens duplicadas organizadas em grupos
│   ├── grupo_0001_md5/     # Grupo de duplicatas exatas
│   │   ├── foto3.jpg
│   │   └── foto3_copia.jpg
│   ├── grupo_0002_phash/   # Grupo de duplicatas visuais
│   │   ├── foto4.jpg
│   │   └── foto4_editada.jpg
│   └── ...
└── organizador_imagens.log # Log do processamento
```

### Como Funciona

1. **Coleta**: O script escaneia o diretório em busca de arquivos de imagem
2. **Hash MD5**: Calcula hash MD5 de cada arquivo para detectar duplicatas exatas
3. **Hash Perceptual**: Calcula hash perceptual de cada imagem para detectar duplicatas visuais
4. **Organização**: 
   - Imagens com MD5 duplicado são agrupadas (cópias exatas)
   - Imagens com hash perceptual duplicado mas MD5 diferente são agrupadas (visualmente similares)
   - Imagens únicas vão para a pasta `validadas`
5. **Preservação**: Todos os arquivos originais são preservados

## Executar Testes

Para executar a suite de testes:

```bash
python test_organizador_imagens.py
```

Para testes mais verbosos:

```bash
python -m pytest test_organizador_imagens.py -v
```

## Dependências

- **Pillow** (>=10.0.0): Processamento de imagens
- **imagehash** (>=4.3.1): Cálculo de hash perceptual

## Logs

O script gera um arquivo de log (`organizador_imagens.log`) com informações detalhadas sobre:
- Número de imagens processadas
- Grupos de duplicatas encontrados
- Estatísticas finais
- Eventuais erros durante o processamento

## Estatísticas de Exemplo

```
==============================================================
ESTATÍSTICAS
==============================================================
Total de imagens processadas: 1500
Imagens únicas (validadas): 1200
Imagens duplicadas (repetidas): 300
Grupos de duplicatas: 45
==============================================================
```

## Formatos Suportados

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **BMP** (.bmp)
- **WEBP** (.webp)

## Otimizações para Performance

- Leitura de arquivos em blocos de 8KB para eficiência de memória
- Processamento paralelo de hashes quando possível
- Logs informativos a cada 100 imagens processadas
- Estrutura de dados otimizada usando `defaultdict`

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Licença

Este projeto é open source e está disponível sob a licença MIT.

## Autor

Kevin William

## Suporte

Para reportar bugs ou solicitar features, por favor abra uma issue no GitHub. 
