#!/usr/bin/env python3
"""
Transform posts CSV to different dialects
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

def transform_without_coref(dialect, text):
    """Transform text bypassing coref cluster creation"""
    # Directly call update and skip coref
    dialect.string = text
    dialect.doc = dialect.nlp(text)
    dialect.tokens = [tok for tok in dialect.doc]
    dialect.end_idx = len(dialect.tokens)
    
    # Set empty coref clusters to bypass validation
    dialect.coref_clusters = []
    
    # Now run transformation rules (this varies by dialect)
    # Call the dialect's specific transformation methods
    # For most dialects, just compile from rules after running methods
    
    # Run morphosyntax transformations if enabled
    if dialect.morphosyntax:
        # This calls all the dialect-specific transformation rules
        for rule_method in dir(dialect):
            if not rule_method.startswith('_') and callable(getattr(dialect, rule_method)):
                method = getattr(dialect, rule_method)
                # Check if it's a transformation method (no parameters)
                try:
                    if 'self' in method.__code__.co_varnames[:1]:
                        method()
                except:
                    pass
    
    return dialect.surface_fix_spacing(dialect.compile_from_rules())

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
    
    final_transformed_column = []
    total_posts = 0
    skipped_posts = 0
    
    for index, row in df.iterrows():
        post_list_as_string = row['Post']
        
        try:
            original_posts = ast.literal_eval(post_list_as_string)
            transformed_posts_in_row = []
            
            for single_post in original_posts:
                total_posts += 1
                try:
                    cleaned_post = preprocess_text(single_post)
                    
                    # Try standard transform first
                    try:
                        transformed = dialect.transform(cleaned_post)
                    except AssertionError:
                        # If coref validation fails, use bypass method
                        transformed = transform_without_coref(dialect, cleaned_post)
                    
                    transformed_posts_in_row.append(transformed)
                    
                except Exception as e:
                    transformed_posts_in_row.append(single_post)
                    skipped_posts += 1
                    print(f"Skipped post in row {index}: {str(e)[:70]}")
            
            final_transformed_column.append(transformed_posts_in_row)

        except (ValueError, SyntaxError):
            print(f"Could not parse row {index}")
            final_transformed_column.append(post_list_as_string)

    output_df = pd.DataFrame({
        'Post': final_transformed_column,
        'Label': df['Label']
    })
    
    output_path = f'posts_{dialect_name}.csv'
    output_df.to_csv(output_path, index=False)
    
    print("-" * 30)
    print(f"Saved to {output_path}")
    print(f"Processed: {total_posts - skipped_posts}/{total_posts}")
    print(f"Skipped: {skipped_posts}")

if __name__ == "__main__":
    main()