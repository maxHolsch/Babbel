"""

Creating images with text for the display

"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
from pathlib import Path

TITLE_SIZE = 50
REGULAR_SIZE = 24
WIDTH_MARGIN = 100
TITLE_Y_OFFSET = 40

LIGHTNESS = 5

CURRENT_PATH = os.path.dirname(__file__)

def create_text_image(region, 
                      width=800,
                      height=480,
                      font_path = os.path.dirname(__file__),
                      text_color=0, 
                      bg_color=255, 
                      background_image=None,
                      line_sequence = False,
                      word_sequence = False,
                      output_path = None):
    
    if word_sequence:
        raise NotImplementedError
    if background_image:
        img = Image.open(background_image)#.convert("RGBA")
        img = img.resize((width, height))

        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(LIGHTNESS)
    else:
        img = Image.new('L', (width, height), bg_color)
    
    draw = ImageDraw.Draw(img)

    # Load font (use default if path is not provided)
    font = ImageFont.truetype(os.path.join(font_path,"Font.ttc"), REGULAR_SIZE)
    font_title = ImageFont.truetype(os.path.join(font_path,"Font.ttc"), TITLE_SIZE)

    # unpack region data
    name, title, text = region

    # Word wrapping
    lines = []
    words = text.split(' ')
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        w = draw.textlength(test_line, font=font)
        if w <= width - WIDTH_MARGIN:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    print(lines)

    # place title
    left, top, right, bottom = draw.textbbox((0,0), title, font=font_title)
    w = abs(left - right)
    h = abs(top - bottom)
    x_title = (width - w) // 2
    draw.text((x_title, TITLE_Y_OFFSET), title, font=font_title, fill=text_color)
    #print(f"title drawn at {x_title, TITLE_Y_OFFSET}")
    title_y = TITLE_Y_OFFSET + h

    # save
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f'constucting direvtory {output_path}')
    
    # Center the text vertically

    total_text_height = 0
    for line in lines:
        left, top, right, bottom = draw.textbbox((0,0), line, font=font)
        total_text_height += abs(top - bottom)
    y_offset = title_y + (height - title_y - total_text_height) // 2
    print('total height',total_text_height, 'offset',y_offset)

    line_num = 0
    word_num = 0 # TODO not yet implemented
    for line in lines :
        left, top, right, bottom = draw.textbbox((0,0),line, font=font)
        #print(left,right,top,bottom)
        w = abs(left - right)
        h = abs(top - bottom)
        #print('w',w,'h',h)
        x = (width - w) // 2
        draw.text((x, y_offset), line, font=font, fill=text_color)
        #print(f"drawn at {x,y_offset}")
        y_offset += h
        line_num += 1

        if line_sequence:
            img.save(os.path.join(output_path,f"{name}_line{line_num}.bmp"))

    if output_path:
        # saving
        img.save(os.path.join(output_path,f"{name}.bmp"))
        print('saving...')
    
    return img

# Example usage
name = "egypt"
title = "Egypt"
text = """This has pyramids."""
img = create_text_image((name,title,text),
                        output_path=os.path.join(CURRENT_PATH,f"{name}"))
img.show()