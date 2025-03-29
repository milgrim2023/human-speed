import sys
import re
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import os
import argparse

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format. Please use YYYY-MM-DD")

def extract_tour_info(url):
    #print(f"Processing URL: {url}")
    
    # Parse the URL
    parsed = urlparse(url)
    #print(f"Parsed URL path: {parsed.path}")
    #print(f"Parsed URL query: {parsed.query}")
    
    # Get query parameters
    params = parse_qs(parsed.query)
    #print(f"Parsed parameters: {params}")
    
    # Extract tour ID from path
    tour_id = parsed.path.split('/')[-1]
    #print(f"Extracted tour ID: {tour_id}")
    
    # Extract share token
    share_token = params.get('share_token', [None])[0]
    print(f"Extracted share token: {share_token}")
    
    if not share_token:
        raise ValueError("No share token found in URL. Make sure the URL contains 'share_token=' parameter")
        
    return tour_id, share_token

def generate_embed_link(tour_id, share_token):
    # Generate the full href and image URL
    href = f"https://www.komoot.com/tour/{tour_id}?share_token={share_token}"
    img_src = f"https://www.komoot.com/tour/{tour_id}/embed?share_token={share_token}&image=1&hm=true&profile=1&width=640&height=700"
    
    html_link = f'<a href="{href}" target="_blank" rel="nofollow noopener noreferrer"><img src="{img_src}" width="640" height="700"/></a>'
    
    return html_link, img_src, href

def download_image(image_url, output_path):
    # Create images directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Downloading image from: {image_url}")
    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Save the image
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"Image saved to: {output_path}")

def generate_markdown(tour_id, clean_href, image_filename, date_str):
    site_baseurl = "{{ site.baseurl }}"
    markdown_content = f"""---
layout: post
title: "{tour_id} Tour"
date: {date_str}
categories: Rides
tags: Bike
---
[![Tour Image]({site_baseurl}/images/posts/{image_filename})](
{clean_href})
"""
    
    # Write the markdown file
    md_filename=f"_posts/{date_str}-route.md"
    with open(md_filename, 'w') as f:
        f.write(markdown_content)
    print(f"Generated {md_filename} file")

def main():
    parser = argparse.ArgumentParser(description='Generate markdown and download images from Komoot tour links')
    parser.add_argument('url', help='Komoot tour URL')
    parser.add_argument('--date', type=validate_date, 
                      help='Date in YYYY-MM-DD format. If not provided, current date will be used')
    
    args = parser.parse_args()
    
    # Use provided date or current date
    date_str = args.date if args.date else datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Extract tour ID and share token
        tour_id, share_token = extract_tour_info(args.url)
        
        # Generate the embed link and get URLs
        embed_link, image_url, clean_href = generate_embed_link(tour_id, share_token)
        
        # Create image filename using provided or current date
        image_filename = f"{date_str}_komoot.png"
        output_path = os.path.join('images', 'posts', image_filename)
        
        # Download the image
        download_image(image_url, output_path)
        
        # Generate the markdown file
        generate_markdown(tour_id, clean_href, image_filename, date_str)
        
        print("\nGenerated HTML link:")
        print(embed_link)
        print(f"\nSuccessfully generated Tour.md and downloaded image to {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
