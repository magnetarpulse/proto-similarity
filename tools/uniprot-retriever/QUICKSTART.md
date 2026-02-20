# Quick Start Guide - UniProt Retriever

## 1. Setup (One-time)

### Install Python dependencies:
```bash
pip install requests biopython pandas
```

### Verify installation:
```bash
python -c "import requests, Bio; print('Ready!')"
```

## 2. Basic Usage

### Download a single protein:
```bash
python uniprot_retriever.py --ids P19338 --output nucleolin.fasta
```

### Download multiple proteins:
```bash
python uniprot_retriever.py --ids P19338 P09651 Q9H2U1 --output proteins.fasta
```

### Download from file:
```bash
# Create file with protein IDs (one per line)
echo "P19338" > my_proteins.txt
echo "P09651" >> my_proteins.txt

# Download
python uniprot_retriever.py --input my_proteins.txt --output sequences.fasta
```

### Search by gene name:
```bash
python uniprot_retriever.py --genes NUCL FUS --organism human --output genes.fasta
```

### Download human proteome:
```bash
python uniprot_retriever.py --proteome UP000005640 --output human_proteome.fasta
```

## 3. For Your AS1411 Project

### Download RG4-binding proteins:
```bash
# Create RG4BP_ids.txt with your protein list
python uniprot_retriever.py --input RG4BP_ids.txt --output RG4_proteins.fasta
```

### Download QUADRatlas validation set:
```bash
python uniprot_retriever.py --input quadratlas_proteins.txt --output quadratlas_sequences.fasta
```

### Search for G-quadruplex proteins:
```bash
python uniprot_retriever.py --query "g-quadruplex OR quadruplex" --organism human --limit 500 --output gquad_proteins.fasta
```

## 4. Check Results

### View downloaded sequences:
```bash
# Windows PowerShell
Get-Content nucleolin.fasta

# Or open in text editor
notepad nucleolin.fasta
```

### Check log file:
```bash
Get-Content uniprot_retrieval.log
```

## 5. Common Issues

**Error: "ModuleNotFoundError"**
→ Run: `pip install requests biopython pandas`

**Error: "Connection timeout"**
→ Check internet connection and try again

**No results found**
→ Verify protein IDs are correct
→ Try adding `--unreviewed` flag

## Need Help?

Check the full README: `README_UniProtRetriever.md`
View log file: `uniprot_retrieval.log`
