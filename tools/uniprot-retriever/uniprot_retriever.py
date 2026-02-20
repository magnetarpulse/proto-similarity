"""
UniProt Sequence Retrieval Program
Author: Simran (for Professor's Research Group)
Date: February 2026
Purpose: Automatically download protein sequences from UniProt database

Features:
- Single or batch protein retrieval
- Multiple input formats (IDs, gene names, search queries)
- Flexible output formats (FASTA, JSON, TSV)
- Error handling and logging
- Support for reviewed/unreviewed filtering
- Organism filtering
- Automatic retry on network failures

Requirements:
    pip install requests biopython pandas

Usage Examples:
    # Single protein by UniProt ID
    python uniprot_retriever.py --ids P19338

    # Multiple proteins from file
    python uniprot_retriever.py --input protein_ids.txt --output sequences.fasta

    # Search by gene names
    python uniprot_retriever.py --genes NUCL NOLC1 --organism human

    # Download entire proteome
    python uniprot_retriever.py --proteome UP000005640 --output human_proteome.fasta

    # Advanced query
    python uniprot_retriever.py --query "reviewed:true AND organism_id:9606" --limit 1000
"""

import requests
import time
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('uniprot_retrieval.log'),
        logging.StreamHandler()
    ]
)

class UniProtRetriever:
    """
    A class to retrieve protein sequences and annotations from UniProt database
    using the official REST API (2026).
    """

    BASE_URL = "https://rest.uniprot.org/uniprotkb"
    POLLING_INTERVAL = 3  # seconds
    MAX_RETRIES = 5

    def __init__(self, email: str = "user@example.com"):
        """
        Initialize the UniProt retriever.

        Args:
            email: Contact email for API requests (good practice)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'Python UniProt Retriever (Contact: {email})'
        })
        self.email = email
        logging.info(f"Initialized UniProt Retriever (Contact: {email})")

    def get_single_entry(self, accession: str, format: str = "fasta") -> Optional[str]:
        """
        Retrieve a single protein entry by UniProt accession.

        Args:
            accession: UniProt accession (e.g., 'P19338')
            format: Output format ('fasta', 'json', 'txt', 'xml')

        Returns:
            String containing the entry data, or None if failed
        """
        url = f"{self.BASE_URL}/{accession}.{format}"

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    logging.info(f"Successfully retrieved {accession}")
                    return response.text
                elif response.status_code == 404:
                    logging.warning(f"Entry {accession} not found")
                    return None
                else:
                    logging.warning(f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed for {accession}: Status {response.status_code}")
                    time.sleep(2 ** attempt)  # Exponential backoff

            except requests.exceptions.RequestException as e:
                logging.error(f"Network error for {accession}: {e}")
                time.sleep(2 ** attempt)

        logging.error(f"Failed to retrieve {accession} after {self.MAX_RETRIES} attempts")
        return None

    def get_batch_entries(self, accessions: List[str], format: str = "fasta", 
                         output_file: Optional[str] = None) -> str:
        """
        Retrieve multiple protein entries efficiently.

        Args:
            accessions: List of UniProt accessions
            format: Output format ('fasta', 'tsv', 'json')
            output_file: Optional output file path

        Returns:
            Combined string of all entries
        """
        logging.info(f"Retrieving {len(accessions)} protein sequences...")

        # Build query for batch retrieval
        accession_query = " OR ".join([f"accession:{acc}" for acc in accessions])

        params = {
            'query': accession_query,
            'format': format,
            'size': 500  # Batch size
        }

        url = f"{self.BASE_URL}/search"
        all_results = []

        try:
            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                result = response.text
                all_results.append(result)

                # Handle pagination if needed
                while 'Link' in response.headers:
                    if 'next' in response.headers['Link']:
                        next_url = self._extract_next_url(response.headers['Link'])
                        response = self.session.get(next_url, timeout=60)
                        if response.status_code == 200:
                            all_results.append(response.text)
                        else:
                            break
                    else:
                        break

                combined_result = "\n".join(all_results)

                if output_file:
                    with open(output_file, 'w') as f:
                        f.write(combined_result)
                    logging.info(f"Results saved to {output_file}")

                logging.info(f"Successfully retrieved {len(accessions)} entries")
                return combined_result
            else:
                logging.error(f"Batch retrieval failed: Status {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during batch retrieval: {e}")
            return ""

    def search_proteins(self, query: str, organism: Optional[str] = None,
                       reviewed: bool = True, limit: int = 100,
                       format: str = "fasta", output_file: Optional[str] = None) -> str:
        """
        Search UniProt with custom query.

        Args:
            query: Search query (e.g., 'gene:NUCL', 'name:nucleolin')
            organism: Organism name or taxon ID (e.g., 'human', '9606')
            reviewed: Limit to reviewed (Swiss-Prot) entries
            limit: Maximum number of results
            format: Output format
            output_file: Optional output file

        Returns:
            Search results as string
        """
        # Build query
        full_query = query

        if organism:
            if organism.lower() in ['human', 'homo sapiens']:
                full_query += " AND organism_id:9606"
            else:
                full_query += f" AND organism:{organism}"

        if reviewed:
            full_query += " AND reviewed:true"

        params = {
            'query': full_query,
            'format': format,
            'size': min(limit, 500)
        }

        logging.info(f"Searching UniProt with query: {full_query}")

        url = f"{self.BASE_URL}/search"
        all_results = []
        retrieved = 0

        try:
            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                result = response.text
                all_results.append(result)
                retrieved += result.count('>')  # Count FASTA entries

                # Pagination
                while 'Link' in response.headers and retrieved < limit:
                    if 'next' in response.headers['Link']:
                        next_url = self._extract_next_url(response.headers['Link'])
                        response = self.session.get(next_url, timeout=60)
                        if response.status_code == 200:
                            all_results.append(response.text)
                            retrieved += response.text.count('>')
                        else:
                            break
                    else:
                        break

                combined_result = "\n".join(all_results)

                if output_file:
                    with open(output_file, 'w') as f:
                        f.write(combined_result)
                    logging.info(f"Results saved to {output_file}")

                logging.info(f"Retrieved {retrieved} protein entries")
                return combined_result
            else:
                logging.error(f"Search failed: Status {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during search: {e}")
            return ""

    def get_proteome(self, proteome_id: str, output_file: str = None) -> str:
        """
        Download entire proteome by proteome ID.

        Args:
            proteome_id: UniProt proteome ID (e.g., 'UP000005640' for human)
            output_file: Output file path

        Returns:
            Proteome sequences as string
        """
        logging.info(f"Downloading proteome {proteome_id}...")

        query = f"proteome:{proteome_id}"
        return self.search_proteins(query, limit=100000, output_file=output_file)

    def get_by_gene_names(self, gene_names: List[str], organism: str = "human",
                         output_file: Optional[str] = None) -> str:
        """
        Retrieve proteins by gene names.

        Args:
            gene_names: List of gene names (e.g., ['NUCL', 'FUS', 'HNRNPA1'])
            organism: Organism filter
            output_file: Output file path

        Returns:
            Protein sequences as string
        """
        gene_query = " OR ".join([f"gene:{gene}" for gene in gene_names])
        return self.search_proteins(gene_query, organism=organism, output_file=output_file)

    def id_mapping(self, ids: List[str], from_db: str = "UniProtKB_AC-ID",
                   to_db: str = "UniProtKB", output_file: Optional[str] = None) -> str:
        """
        Map IDs between different databases.

        Args:
            ids: List of IDs to map
            from_db: Source database (e.g., 'Gene_Name', 'EMBL', 'RefSeq_Protein')
            to_db: Target database (default: UniProtKB)
            output_file: Output file path

        Returns:
            Mapping results
        """
        url = "https://rest.uniprot.org/idmapping/run"

        data = {
            'ids': ','.join(ids),
            'from': from_db,
            'to': to_db
        }

        logging.info(f"Submitting ID mapping job for {len(ids)} IDs...")

        try:
            # Submit job
            response = self.session.post(url, data=data, timeout=30)

            if response.status_code == 200:
                job_id = response.json()['jobId']
                logging.info(f"Job submitted: {job_id}")

                # Poll for results
                status_url = f"https://rest.uniprot.org/idmapping/status/{job_id}"

                while True:
                    status_response = self.session.get(status_url, timeout=30)

                    if status_response.status_code == 200:
                        status_data = status_response.json()

                        if 'results' in status_data or 'failedIds' in status_data:
                            # Job complete
                            results_url = f"https://rest.uniprot.org/idmapping/results/{job_id}?format=fasta"
                            results = self.session.get(results_url, timeout=60)

                            if results.status_code == 200:
                                result_text = results.text

                                if output_file:
                                    with open(output_file, 'w') as f:
                                        f.write(result_text)
                                    logging.info(f"Mapping results saved to {output_file}")

                                logging.info("ID mapping completed successfully")
                                return result_text
                            else:
                                logging.error(f"Failed to retrieve results: Status {results.status_code}")
                                return ""
                        else:
                            logging.info("Job still running, waiting...")
                            time.sleep(self.POLLING_INTERVAL)
                    else:
                        logging.error(f"Status check failed: Status {status_response.status_code}")
                        return ""
            else:
                logging.error(f"Failed to submit job: Status {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during ID mapping: {e}")
            return ""

    @staticmethod
    def _extract_next_url(link_header: str) -> Optional[str]:
        """Extract next URL from Link header."""
        parts = link_header.split(',')
        for part in parts:
            if 'rel="next"' in part:
                url = part.split(';')[0].strip('<> ')
                return url
        return None


def read_ids_from_file(file_path: str) -> List[str]:
    """Read protein IDs from text file (one per line)."""
    ids = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                ids.append(line)
    return ids


def main():
    parser = argparse.ArgumentParser(
        description='Retrieve protein sequences from UniProt database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single protein
  python uniprot_retriever.py --ids P19338 --output nucleolin.fasta

  # Multiple proteins from file
  python uniprot_retriever.py --input protein_ids.txt --output sequences.fasta

  # Search by gene names
  python uniprot_retriever.py --genes NUCL FUS HNRNPA1 --organism human --output rg4_proteins.fasta

  # Download proteome
  python uniprot_retriever.py --proteome UP000005640 --output human_proteome.fasta

  # Custom search
  python uniprot_retriever.py --query "annotation:(type:rna-bind)" --organism human --limit 500
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--ids', nargs='+', help='UniProt accession(s)')
    input_group.add_argument('--input', help='File containing UniProt IDs (one per line)')
    input_group.add_argument('--genes', nargs='+', help='Gene name(s)')
    input_group.add_argument('--query', help='Custom UniProt query')
    input_group.add_argument('--proteome', help='Proteome ID (e.g., UP000005640)')

    # Filter options
    parser.add_argument('--organism', default=None, help='Organism filter (e.g., human, 9606)')
    parser.add_argument('--reviewed', action='store_true', default=True, 
                       help='Only reviewed (Swiss-Prot) entries (default: True)')
    parser.add_argument('--unreviewed', action='store_true', 
                       help='Include unreviewed (TrEMBL) entries')

    # Output options
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--format', default='fasta', 
                       choices=['fasta', 'json', 'tsv', 'xml'],
                       help='Output format (default: fasta)')
    parser.add_argument('--limit', type=int, default=500, 
                       help='Maximum number of results (default: 500)')

    # Other options
    parser.add_argument('--email', default='user@example.com',
                       help='Contact email for API requests')

    args = parser.parse_args()

    # Initialize retriever
    retriever = UniProtRetriever(email=args.email)

    # Handle unreviewed flag
    reviewed = args.reviewed and not args.unreviewed

    # Execute appropriate retrieval method
    try:
        if args.ids:
            if len(args.ids) == 1:
                result = retriever.get_single_entry(args.ids[0], format=args.format)
                if result:
                    with open(args.output, 'w') as f:
                        f.write(result)
            else:
                retriever.get_batch_entries(args.ids, format=args.format, 
                                          output_file=args.output)

        elif args.input:
            ids = read_ids_from_file(args.input)
            logging.info(f"Read {len(ids)} IDs from {args.input}")
            retriever.get_batch_entries(ids, format=args.format, 
                                      output_file=args.output)

        elif args.genes:
            retriever.get_by_gene_names(args.genes, organism=args.organism or "human",
                                      output_file=args.output)

        elif args.query:
            retriever.search_proteins(args.query, organism=args.organism,
                                    reviewed=reviewed, limit=args.limit,
                                    format=args.format, output_file=args.output)

        elif args.proteome:
            retriever.get_proteome(args.proteome, output_file=args.output)

        logging.info(f"\nRetrieval complete! Results saved to: {args.output}")
        logging.info(f"Log file: uniprot_retrieval.log")

    except Exception as e:
        logging.error(f"Error during retrieval: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
