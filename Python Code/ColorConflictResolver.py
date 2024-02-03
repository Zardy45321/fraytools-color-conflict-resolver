## Fraytools Color Conflict Resolver V1
## Created by: Zardy Z

## Imports
import PySimpleGUI as sg
import json
import os
import shutil
from PIL import Image
import numpy as np
import collections


'''Read JSON contents from given path'''
def getJSONData(path: str):
    with open(path,'r') as file:
        return json.load(file)

'''Creates the Fray Theme'''
fray_theme = {'BACKGROUND': '#323232',
             'TEXT': '#e2eef5',
             'INPUT': '#585858',
             'TEXT_INPUT': '#cecad0',
             'SCROLL': '#585858',
             'BUTTON': ('#e2eef5', '#585858'),
             'PROGRESS': ('#f5ba04', '#6b6b6b'),
             'BORDER': 1,
             'SLIDER_DEPTH': 0,
             'PROGRESS_DEPTH': 0}

sg.theme_add_new('fraymakers', fray_theme)                   

sg.theme('fraymakers')
sg.set_options(font=('Calibri',12))


'''Window Functions'''
def update_visibility(elements: dict):
    '''
    Updates the visibility
    of specified elements
    '''
    global window
    for k,v in elements.items():
        window[k].update(visible=v)

def update_table_values(table_name: str):
    '''
    Updates table values
    based upon table name
    '''
    global window
    
    window['db_table'].update(values=anim_indexes)
    
    return anim_indexes

def update_disabled(elements: dict):
    '''
    Updates the disabled
    status of buttons
    '''
    global window
    for k,v in elements.items():
        window[k].update(disabled=v)
    
                                   
def ez_fix_all(path:str,new_path:str,palette_path:str):
    if path != new_path:
        shutil.copytree(path,new_path,dirs_exist_ok=True)
    
    all_colors = []
    for subdir, dirs, files in os.walk(new_path):
        for f in files:
            if '.png' in f and '.meta' not in f:
                file_path = os.path.join(path,subdir,f)
                all_colors.extend(getColors(file_path))

    all_colors = [[x[0],x[1],x[2]] for x in all_colors]
    #print(all_colors)         
    mytuplelist = [tuple(item) for item in all_colors]
    all_colors = list(set(mytuplelist))
    test_colors = [[x[0],x[1]] for x in all_colors]
    print(len(all_colors))
    mytuplelist = [tuple(item) for item in test_colors]
    test_colors = list(set(mytuplelist))
    print(len(test_colors))
    print(test_colors)
    bad_colors = getBadColors(all_colors)
    mytuplelist = [tuple(item) for item in bad_colors]
    bad_colors = list(set(mytuplelist))
    print(len(bad_colors))
    print(bad_colors)

    fixed_colors = {}
    fixed_hexes = {}
    
    for subdir, dirs, files in os.walk(new_path):
        for f in files:
            if '.png' in f and '.meta' not in f:
                print(f)
                file_path = os.path.join(path,subdir,f)
                colors = getColors(file_path)
                #alpha = [x[3] for x in colors]
                colors = [[x[0],x[1]] for x in colors]
                
                image_data = getImageData(file_path)
                for c in colors:
                    for b in bad_colors:
                         if b[0] == c[0] and b[1] == c[1]:     
                    
                            
                            mode = 'add'
                            good_color = False
                            new_color = c[0]
                            while good_color == False:
                                if mode == 'add':
                                    new_color += 1
                                else:
                                    new_color -= 1
                                    
                                if new_color > 255:
                                    mode = 'sub'
                                    new_color = c[0]-1
                                    
                                bad_match = False
                                if (new_color,c[1]) in test_colors:
                                    bad_match = True

                                if str(new_color)+','+str(c[1]) in list(fixed_colors.keys()):
                                    if b[2] != fixed_colors[str(new_color)+','+str(c[1])]:
                                        bad_match = True

                                if bad_match == False:

                                    fixed_colors[str(new_color)+','+str(c[1])] = b[2]
                                    fixed_hexes[rgb2hex(b[0],b[1],b[2])] = rgb2hex(new_color,b[1],b[2])
                                    image_data = recolorImage(image_data,[b[0],b[1],b[2]],[new_color,b[1],b[2]])
                                    #test_colors.append((new_color,b[1]))
                                    #print(test_colors)
                                    #exit()
                                    good_color = True
                                    

                new_save_path = os.path.join(new_path,subdir,f)
                saveNewImage(new_save_path,image_data)

    print(fixed_hexes)
    palette_json = getJSONData(palette_path)
    colors = palette_json['colors']
    i = 0
    for c in colors:
        start_color = c['color'][:4]
        end_color = c['color'][4:]
        for k,v in fixed_hexes.items():
            if k == end_color:
                colors[i]['color'] = start_color+v
        i += 1

    palette_json['colors'] = colors

    maps = palette_json['maps']
    i = 0
    for m in maps:
        i2 = 0
        for c in m['colors']:
            start_color = c['targetColor'][:4]
            end_color = c['targetColor'][4:]
            for k,v in fixed_hexes.items():
                if k == end_color:
                    maps[i]['colors'][i2]['targetColor'] = start_color+v

            i2 += 1
        i += 1

    palette_json['maps'] = maps
        
    with open(palette_path, 'w') as f:
        json.dump(palette_json, f, indent=4)
        


'''Image Functions'''
def getColors(path:str):
    img = Image.open(path)
    colors = img.convert('RGBA').getcolors()
    colors = [c[1] for c in colors]
    return colors


def getImageData(path:str):
    im = Image.open(path)
    im = im.convert('RGBA')
    data = np.array(im)
    return data

def rgb2hex(r,g,b):
    return "{:02x}{:02x}{:02x}".format(r,g,b).upper()

def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))


def getBadColors(colors:list):
    rg_colors = []
    bad_colors = []
    #print(colors)
    for c in colors:
        color_match = False
        for rg in rg_colors:
            #print(rg_colors)
            if rg[0] == c[0] and rg[1] == c[1]:
                
                if [c[0],c[1],c[2]] not in bad_colors:
                    bad_colors.append([c[0],c[1],c[2]])
                color_match = True

        if color_match == False:
            rg_colors.append([c[0],c[1]])

    #print(bad_colors)
    return bad_colors


def recolorImage(data:list, old_color:list, new_color:list):

    r1, g1, b1 = old_color[0], old_color[1], old_color[2] # Original value
    r2, g2, b2 = new_color[0], new_color[1], new_color[2] # Value that we want to replace it with

    red, green, blue = data[:,:,0], data[:,:,1], data[:,:,2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    data[:,:,:3][mask] = [r2, g2, b2]
    return data


def saveNewImage(save_path,data):
    im = Image.fromarray(data)
    im.save(save_path)


ez_fix_all_layout = [[sg.Text('Sprite Folder',font=('Edit Undo BRK',18)),
                      sg.InputText(key='batch_sprite_folder',size=25),
                      sg.FolderBrowse(key='sprite_folder')],
                     [sg.Text('New Sprite Folder',font=('Edit Undo BRK',18)),
                      sg.InputText(key='new_sprite_folder',size=25),
                      sg.FolderBrowse(key='sprite_folder_new')],
                     [sg.Text('Palette File',font=('Edit Undo BRK',18)),
                      sg.InputText(key='palette_file',size=25),
                      sg.FileBrowse(key='palette_file_path')]]

start_layout = [[sg.Column(ez_fix_all_layout,key='ez_fix_all_layout')],
                [sg.Button('Go',key='go'),sg.Button('Exit')]]

layout = [[sg.Text('Color Conflict Resolver V1.0', justification='center',font=('Centie Sans',26))],
          [sg.Column(start_layout, key='Start Layout', element_justification='c')]]
          

window = sg.Window('Fraytools Color Conflict Resolver',layout,element_justification = 'center')

while True:
    event, values = window.read()
    print(event)
    if event == None or event == 'Exit':
        window.close()
        break

    elif event == 'go':
        ez_fix_all(values['batch_sprite_folder'],values['new_sprite_folder'],values['palette_file'])
        sg.popup('Sprites Fixed!')
        window.close()
        break
        

                    
            
            
        
        
                

        
        
        
        
        
