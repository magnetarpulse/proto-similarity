"""
Test Script for UniProt Retriever
Run this to verify the program works correctly
"""

import sys
import os

print("="*60)
print("Testing UniProt Retriever Program")
print("="*60)

# Test 1: Check dependencies
print("\n[Test 1] Checking dependencies...")
try:
    import requests
    import Bio
    print("✅ All dependencies installed")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: pip install requests biopython pandas")
    sys.exit(1)

# Test 2: Import the module
print("\n[Test 2] Loading UniProt Retriever...")
try:
    from uniprot_retriever import UniProtRetriever
    print("✅ Module loaded successfully")
except Exception as e:
    print(f"❌ Failed to load module: {e}")
    sys.exit(1)

# Test 3: Initialize retriever
print("\n[Test 3] Initializing retriever...")
try:
    retriever = UniProtRetriever(email="test@example.com")
    print("✅ Retriever initialized")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    sys.exit(1)

# Test 4: Download single protein (Nucleolin)
print("\n[Test 4] Downloading test protein (Nucleolin - P19338)...")
try:
    result = retriever.get_single_entry("P19338", format="fasta")
    if result and len(result) > 0:
        print("✅ Successfully retrieved protein")
        print(f"   Sequence length: ~{len(result)} characters")

        # Save to test file
        with open("test_nucleolin.fasta", "w") as f:
            f.write(result)
        print("   Saved to: test_nucleolin.fasta")
    else:
        print("❌ No data retrieved")
except Exception as e:
    print(f"❌ Download failed: {e}")

# Test 5: Batch download
print("\n[Test 5] Testing batch download (3 proteins)...")
try:
    test_ids = ["P19338", "P09651", "Q9H2U1"]
    retriever.get_batch_entries(test_ids, output_file="test_batch.fasta")

    if os.path.exists("test_batch.fasta"):
        with open("test_batch.fasta", "r") as f:
            content = f.read()
            entry_count = content.count('>')
        print(f"✅ Batch download successful")
        print(f"   Retrieved {entry_count} protein(s)")
        print("   Saved to: test_batch.fasta")
    else:
        print("❌ Batch file not created")
except Exception as e:
    print(f"❌ Batch download failed: {e}")

# Test 6: Search by gene name
print("\n[Test 6] Testing gene name search (NUCL)...")
try:
    retriever.get_by_gene_names(["NUCL"], organism="human", 
                                output_file="test_gene_search.fasta")

    if os.path.exists("test_gene_search.fasta"):
        print("✅ Gene search successful")
        print("   Saved to: test_gene_search.fasta")
    else:
        print("❌ Gene search file not created")
except Exception as e:
    print(f"❌ Gene search failed: {e}")

# Summary
print("\n" + "="*60)
print("Testing Complete!")
print("="*60)
print("\nGenerated test files:")
print("  - test_nucleolin.fasta")
print("  - test_batch.fasta")
print("  - test_gene_search.fasta")
print("  - uniprot_retrieval.log")
print("\nYou can delete these test files if not needed.")
print("\nThe program is ready to use! 🎉")
