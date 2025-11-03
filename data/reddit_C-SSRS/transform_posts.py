#!/usr/bin/env python3
"""
Transform posts CSV to different dialects with detailed tracking
Usage: python transform_posts.py <dialect_name>
Example: python transform_posts.py AfricanAmericanVernacular
"""

import sys
import pandas as pd
import ast
import re
from multivalue import Dialects

def preprocess_text(text):
    """Clean text for better tokenization"""
    text = text.replace('""', '"')
    text = re.sub(r'\.{2,}', '. ', text)
    text = re.sub(r'([.!?:])(["\']?)([A-Za-z])', r'\1\2 \3', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    if len(sys.argv) != 2:
        print("Usage: python transform_posts.py <dialect_name>")
        sys.exit(1)
    
    dialect_name = sys.argv[1]
    
    # Read input CSV
    df = pd.read_csv('posts_SAE.csv').head(5)
    
    # Initialize dialect
    dialect_class = getattr(Dialects, dialect_name)
    dialect = dialect_class()
    
    # Store results for each individual post
    results = []
    skipped = 0
    
    for user_idx, row in df.iterrows():
        post_list_as_string = row['Post']
        label = row['Label']
        
        try:
            original_posts = ast.literal_eval(post_list_as_string)
            
            for single_post in original_posts:
                try:
                    # Preprocess
                    preprocessed = preprocess_text(single_post)
                    
                    # Transform with fallback
                    try:
                        transformed = dialect.transform(preprocessed)
                        rules_applied = str(dialect.executed_rules)
                    except AssertionError:
                        # Coref validation failed - keep original
                        transformed = preprocessed
                        rules_applied = "SKIPPED: Tokenization mismatch"
                        skipped += 1
                    
                    # Store result
                    results.append({
                        'User': f'User_{user_idx}',
                        'Label': label,
                        'Original_Post': single_post,
                        'Preprocessed_SAE': preprocessed,
                        f'{dialect_name}_Prompt': transformed,
                        'Rules_Applied': rules_applied
                    })
                    
                except Exception as e:
                    # Other errors - keep original
                    results.append({
                        'User': f'User_{user_idx}',
                        'Label': label,
                        'Original_Post': single_post,
                        'Preprocessed_SAE': preprocess_text(single_post),
                        f'{dialect_name}_Prompt': single_post,
                        'Rules_Applied': f"ERROR: {str(e)[:50]}"
                    })
                    skipped += 1
        
        except (ValueError, SyntaxError) as e:
            print(f"Could not parse row {user_idx}: {e}")
    
    # Create output dataframe
    output_df = pd.DataFrame(results)
    
    # Save
    output_path = f'posts_{dialect_name}_detailed.csv'
    output_df.to_csv(output_path, index=False)
    
    print("-" * 40)
    print(f"Saved to {output_path}")
    print(f"Total posts: {len(results)}")
    print(f"Successfully transformed: {len(results) - skipped}")
    print(f"Skipped/Failed: {skipped}")

if __name__ == "__main__":
    main()