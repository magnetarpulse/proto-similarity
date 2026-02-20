# UniProt Sequence Retrieval Program

**Author:** Simran  
**Date:** February 2026  
**Purpose:** Automated protein sequence retrieval from UniProt database

## Overview

This program provides a comprehensive Python interface to the UniProt REST API (2026) for automated retrieval of protein sequences and annotations. It supports single/batch downloads, custom queries, proteome downloads, and ID mapping.

## Features

✅ **Single or batch protein retrieval** - Download one or thousands of proteins  
✅ **Multiple input formats** - UniProt IDs, gene names, or custom queries  
✅ **Flexible output formats** - FASTA, JSON, TSV, XML  
✅ **Organism filtering** - Species-specific searches  
✅ **Reviewed/unreviewed filtering** - Swiss-Prot or TrEMBL  
✅ **Error handling** - Automatic retry with exponential backoff  
✅ **Logging** - Detailed logs of all operations  
✅ **Pagination support** - Handle large result sets automatically  
✅ **ID mapping** - Convert between different database identifiers  

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection

### Install Dependencies

```bash
pip install requests biopython pandas
```

Or use the provided requirements file:

```bash
pip install -r requirements.txt
```

## Usage Examples

### 1. Single Protein by UniProt ID

```bash
python uniprot_retriever.py --ids P19338 --output nucleolin.fasta
```

**Output:** Single FASTA file with Nucleolin sequence

### 2. Multiple Proteins (Command Line)

```bash
python uniprot_retriever.py --ids P19338 P09651 Q9H2U1 --output proteins.fasta
```

**Output:** FASTA file with all three protein sequences

### 3. Batch Download from File

Create a text file `protein_ids.txt`:
```
P19338
P09651
Q9H2U1
P35637
P06748
```

Run:
```bash
python uniprot_retriever.py --input protein_ids.txt --output batch_proteins.fasta
```

### 4. Search by Gene Names

```bash
python uniprot_retriever.py --genes NUCL FUS HNRNPA1 DHX36 --organism human --output rg4_proteins.fasta
```

**Output:** Proteins matching those gene names in human

### 5. Download Entire Proteome

```bash
# Human reviewed proteome (Swiss-Prot)
python uniprot_retriever.py --proteome UP000005640 --output human_reviewed.fasta

# Mouse proteome
python uniprot_retriever.py --proteome UP000000589 --output mouse_proteome.fasta
```

### 6. Custom Search Query

```bash
# All RNA-binding proteins in human
python uniprot_retriever.py --query "annotation:(type:rna-bind)" --organism human --limit 1000 --output rna_binding_proteins.fasta

# All G-quadruplex related proteins
python uniprot_retriever.py --query "g-quadruplex OR quadruplex" --organism human --output gquad_proteins.fasta

# Proteins in nucleus
python uniprot_retriever.py --query "locations:(location:nucleus)" --organism 9606 --limit 500 --output nuclear_proteins.fasta
```

### 7. Different Output Formats

```bash
# JSON format (detailed annotations)
python uniprot_retriever.py --ids P19338 --output nucleolin.json --format json

# TSV format (tabular data)
python uniprot_retriever.py --genes NUCL FUS --output proteins.tsv --format tsv --organism human
```

### 8. Include Unreviewed Entries

```bash
python uniprot_retriever.py --genes NOLC1 --organism human --unreviewed --output nolc1_all.fasta
```

## Command Line Arguments

### Required Arguments (choose one):

| Argument | Description | Example |
|----------|-------------|---------|
| `--ids` | One or more UniProt accessions | `--ids P19338 P09651` |
| `--input` | File with IDs (one per line) | `--input ids.txt` |
| `--genes` | One or more gene names | `--genes NUCL FUS` |
| `--query` | Custom UniProt search query | `--query "name:nucleolin"` |
| `--proteome` | Proteome ID | `--proteome UP000005640` |

### Optional Arguments:

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--output`, `-o` | Output file path | **Required** | `-o output.fasta` |
| `--organism` | Organism filter | None | `--organism human` |
| `--reviewed` | Only reviewed entries | True | `--reviewed` |
| `--unreviewed` | Include unreviewed | False | `--unreviewed` |
| `--format` | Output format | fasta | `--format json` |
| `--limit` | Max results | 500 | `--limit 1000` |
| `--email` | Contact email | user@example.com | `--email me@uni.edu` |

## Common Proteome IDs

| Organism | Proteome ID | Description |
|----------|-------------|-------------|
| Human | UP000005640 | Homo sapiens (reviewed) |
| Mouse | UP000000589 | Mus musculus |
| Rat | UP000002494 | Rattus norvegicus |
| E. coli | UP000000625 | Escherichia coli K-12 |
| Yeast | UP000002311 | Saccharomyces cerevisiae |
| Fruit fly | UP000000803 | Drosophila melanogaster |
| C. elegans | UP000001940 | Caenorhabditis elegans |

## UniProt Query Language

### Search by Protein Name
```
name:nucleolin
```

### Search by Gene
```
gene:NUCL
```

### Search by Annotation
```
annotation:(type:rna-bind)
annotation:(type:"DNA binding")
```

### Search by Location
```
locations:(location:nucleus)
locations:(location:cytoplasm)
```

### Search by Organism
```
organism_id:9606  # Human
organism:"Homo sapiens"
```

### Combined Queries
```
gene:FUS AND organism_id:9606 AND reviewed:true
(gene:NUCL OR gene:FUS) AND annotation:(type:rna-bind)
```

## Output Files

### FASTA Format (default)
```
>sp|P19338|NUCL_HUMAN Nucleolin OS=Homo sapiens OX=9606 GN=NCL PE=1 SV=3
MKNKGFSDKDDDDSRKKKDVNGPDFKKKGEGVKKRKTREKTSSDQVPKRDKVDKAPGKQK
KMAPKKEKDKDQAQKTKMRPAKEKPAKKAGGKKQAGKPGGKKKAGKPGKKKKAAGASDK...
```

### JSON Format
Contains detailed annotations, features, sequences, cross-references, etc.

### TSV Format
Tab-separated table with selected fields.

## Logging

All operations are logged to `uniprot_retrieval.log`:

```
2026-02-17 10:40:15 - INFO - Initialized UniProt Retriever (Contact: user@example.com)
2026-02-17 10:40:16 - INFO - Retrieving 5 protein sequences...
2026-02-17 10:40:18 - INFO - Successfully retrieved 5 entries
2026-02-17 10:40:18 - INFO - Results saved to output.fasta
```

## Error Handling

The program includes:
- **Automatic retry** with exponential backoff (up to 5 attempts)
- **Network error handling** with detailed logging
- **404 detection** for non-existent entries
- **Timeout protection** (30-60 seconds per request)

## Use Cases for Your AS1411 Project

### 1. Download RG4-Binding Proteins
```bash
# Download your validation set
python uniprot_retriever.py --input RG4BP_ids.txt --output RG4_proteins.fasta
```

### 2. Download QUADRatlas Proteins
```bash
# After getting IDs from QUADRatlas
python uniprot_retriever.py --input quadratlas_proteins.txt --output quadratlas_sequences.fasta
```

### 3. Download Human Reviewed Proteome
```bash
# For embedding analysis
python uniprot_retriever.py --proteome UP000005640 --output human_reviewed.fasta
```

### 4. Validate Top Candidates
```bash
# Get sequences for your top 50 candidates
python uniprot_retriever.py --input top50_candidates.txt --output candidates_sequences.fasta
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'requests'"
**Solution:** Install dependencies: `pip install requests`

### Issue: "Connection timeout"
**Solution:** Check internet connection. Program will retry automatically.

### Issue: "No results found"
**Solution:** 
- Verify protein IDs are correct
- Check organism filter
- Try `--unreviewed` flag for newer/predicted proteins

### Issue: "Too many results"
**Solution:** Use `--limit` to specify maximum: `--limit 1000`

## API Rate Limits

UniProt API is free but has reasonable usage limits:
- **Be respectful**: Don't hammer the server
- **Batch requests**: Use file input for multiple IDs
- **Set email**: Use `--email` for better support if issues arise

## Advanced: Using as Python Module

```python
from uniprot_retriever import UniProtRetriever

# Initialize
retriever = UniProtRetriever(email="your.email@university.edu")

# Single protein
sequence = retriever.get_single_entry("P19338", format="fasta")

# Batch download
accessions = ["P19338", "P09651", "Q9H2U1"]
retriever.get_batch_entries(accessions, output_file="proteins.fasta")

# Search
retriever.search_proteins(
    query="annotation:(type:rna-bind)",
    organism="human",
    limit=100,
    output_file="rna_binding.fasta"
)

# Gene names
retriever.get_by_gene_names(
    ["NUCL", "FUS", "HNRNPA1"],
    organism="human",
    output_file="genes.fasta"
)

# Proteome
retriever.get_proteome("UP000005640", output_file="human_proteome.fasta")
```

## Support

- **UniProt Help:** https://www.uniprot.org/help/
- **UniProt API Documentation:** https://www.uniprot.org/help/api
- **Contact:** Check `uniprot_retrieval.log` for detailed error messages

## Citation

If you use this program in your research, please cite:

**UniProt Database:**
> UniProt Consortium. "UniProt: the Universal Protein Knowledgebase in 2025." 
> Nucleic Acids Research (2025).

**This Tool:**
> Developed for AS1411-Ankh research project, February 2026.

## License

This program is provided for academic and research purposes.

---

**Created by:** Simran  
**For:** Professor's Research Group  
**Date:** February 17, 2026  
**Project:** AS1411-Ankh Integrated Discovery Pipeline
