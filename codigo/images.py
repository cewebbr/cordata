#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Functions for preparing representative images for usecases in CORDATA.
Copyright (C) 2026  Henrique S. Xavier
Contact: contato@henriquexavier.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import requests
from io import BytesIO
from PIL import Image, ImageOps
from pathlib import Path


def http_get(url, max_retries=3, timeout=10):
    """
    Make an HTTP GET request to `url` (str) and return a response object.

    Parameters
    ----------
    url : str
        The Web Address to request.
    max_retries : int
        Maximum number of request trials before giving up.
    timeout : float
        How long to wait for a response, in seconds.
    """
    # Prepare for request:
    session = requests.session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=max_retries))
    
    # GET:
    ssl_verify = True
    try:
        response = session.get(url, timeout=timeout)
    # In case of SSL Certificate error:
    except requests.exceptions.SSLError:
        ssl_verify = False
        response = session.get(url, timeout=timeout, verify=ssl_verify)

    # If forbidden, try pretending to be a browser:
    if response.status_code in {403, 404, 406, 412, 503, 429}:
        browser_header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'}
        response = session.get(url, timeout=timeout, headers=browser_header, verify=ssl_verify)
    
    # If fail:
    if response.status_code != 200:
        raise Exception('HTTP request failed with code ' + str(response.status_code))

    return response


def standardize_image_from_url(url, output_path, target_height=293, target_width=523, grayband_factor=1):
    """
    Downloads an image from the Web and standardizes it to a target aspect ratio and size.

    Steps:
    1. Downloads JPG, PNG, or GIF image from URL.
    2. Computes current aspect ratio.
    3. Crops or pads symmetrically based on deviation from target aspect ratio.
    4. Scales image to target width while maintaining aspect ratio.
    5. Saves output as PNG.

    Parameters
    ----------
    url : str 
        URL of the image.
    output_path : str 
        Path to save transformed PNG image.
    target_height : int
        Target height in pixels.
    target_width : int
        Target width in pixels.
    grayband_factor : float
        Aspect ratio (width / height) factor between the current and target image 
        up to which a gray band is added to it instead of cropping.  It must be
        greater than or equal to one. If set to 1, the image is always cropped to 
        reach the desired aspect ratio.
    """
    # Step 1: Download image from URL
    response = http_get(url)
    response.raise_for_status()  # Raises error for invalid response
    if response.headers.get("Content-Type")[:9] != 'text/html':
        #print(response.headers.get("Content-Type"))
        img = Image.open(BytesIO(response.content)).convert("RGB")
    
        # Compute image and target aspect ratios
        width, height = img.size
        aspect = width / height
        target_aspect = target_width / target_height
    
        # Step 3: If aspect ratio is more than the required on the target, crop horizontally:
        if aspect > grayband_factor * target_aspect:
            new_width = int(height * target_aspect)
            left = (width - new_width) // 2
            right = left + new_width
            img = img.crop((left, 0, right, height))
            width, height = img.size
            aspect = width / height
    
        # Step 4: If aspect ratio is less than required on the target, crop vertically:
        elif aspect < target_aspect / grayband_factor:
            new_height = int(width / target_aspect)
            top = (height - new_height) // 2
            bottom = top + new_height
            img = img.crop((0, top, width, bottom))
            width, height = img.size
            aspect = width / height
    
        # Step 5: If slightly wider, add gray bands on top/bottom:
        elif aspect > target_aspect:
            new_height = int(width / target_aspect)
            padding = (new_height - height) // 2
            img = ImageOps.expand(img, border=(0, padding, 0, padding), fill=(128, 128, 128))
            width, height = img.size
    
        # Step 6: If slightly narrower, add gray bands on left/right:
        elif aspect < target_aspect:
            new_width = int(height * target_aspect)
            padding = (new_width - width) // 2
            img = ImageOps.expand(img, border=(padding, 0, padding, 0), fill=(128, 128, 128))
            width, height = img.size
    
        # Step 7: Scale image to have target width (keeping aspect):
        new_height = int((target_width / width) * height)
        img = img.resize((target_width, new_height), Image.LANCZOS)
    
        # Step 8: Save as PNG
        img.save(output_path, format="PNG")

        return True
        
    else:
        return False
    

def etl_usecase_image(uc : dict, outfolder='../imagens/', outfile_template='hash_id_%(hash_id)s.png', 
                      url_path='https://raw.githubusercontent.com/cewebbr/cordata/main/imagens/', 
                      skip_pattern='raw.githubusercontent.com/cewebbr/cordata/', verbose=False):

    # Only process usecase images that are not in CORDATA's github
    # (that is, that were not processes already and that are not the default image):
    if uc['url_image'].find(skip_pattern) == -1:
        
        # Set local path to new image:
        outfile = outfile_template % uc
        outpath = Path(outfolder) / Path(outfile)
        if verbose == True:
            print(f"Will standardize {uc['url_image']} to {outpath}.")
        # Standardize new image:
        success = standardize_image_from_url(uc['url_image'], outpath)
        
        # Set URL for new image:
        if success == True:
            if verbose == True:
                url_image = f"{url_path}{outfile}"
                print(f'Will set url_image to {url_image}.')
            uc['url_image'] = url_image
        # Keep original URL if new image failed.
        elif verbose == True:
            print('Standardization failed!')

    elif verbose == True:
        print(f"Skipping {uc['hash_id']} ({uc['url_image']}).")