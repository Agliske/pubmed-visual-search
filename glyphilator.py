import numpy as np 
import pandas as pd
import math
import difflib
import os
from sklearn.preprocessing import MinMaxScaler
#import spacy #for natural language processing ie. when I want to include context-aware word searching

#usage order: 
# need articleData: list of dict containing title,url,content,date of each article. 
# need wordlists: collection of .txt files inside of the \wordlists folder containing "\n" (newline) separated words or phrases to search for within content of article.

#code:
#wordlists = wordlists_from_folder(filepath)                     #absolute filepath to the folder containing the wordlists
#allGlyphData = generateGlyphInput(articleData,wordlists)        #creates the list of lists used as input to size glyph toroids for each article
#antzfile = constructBasicGlyphs(allGlyphData)                   #creates antz-readable CSV node file. The user just needs to put it into a directory openable by antz.



cwd = os.getcwd()

def wordlist_from_txtFile(filepath):
    """_summary_

    Args:
        filepath (string): absolute filepath to your txt file

    Returns:
        lines (list of string): list containing string of each new line of the txt file
    """

    with open(filepath, "r") as file:
        text = file.read()
        lines = text.split("\n")
    
    
    return lines

def wordlists_from_folder(dirpath):
    
    files = os.listdir(dirpath)
    

    list_txt_filepaths = []
    for file in files:
        if file.endswith('.txt'):
            list_txt_filepaths.append(dirpath + r"\\" + file)
    
    
    wordlists = []
    for file in list_txt_filepaths:
        wordlist = wordlist_from_txtFile(file)
        wordlists.append(wordlist)

    return wordlists

def generateGlyphInput(articleData, wordlists, search_metadata = {
                                            "geometrySelection": "Toroid", 
                                            "wordlist_paths" : ["path/to/WL1.txt","path/to/WL2.txt","path/to/WL3.txt"],
                                            "search_string": "sample string",
                                            "num_results_requested": 200,
                                            "scaling_range": (0.2,2.5),
                                            "scaling_type": "minmax"}):
    """
    generateGlyphInput _summary_

    Args:
        articleData (list of dict): each dict contains content and metadata, all stacked in a list of results for multiple articles
        wordlists (list of list): each element of list is one list of strings, containing search terms for a particular subject
        search_metadata(dict): 

    Returns:
        (list of list): list of list containing floats, which scale each glyph element
    """

    allGlyphData = [] #list of lists. List of all of the information needed to build all glyphs with the specified wordlists. Each element in list corresponds to the info to build one glyph.
    for i in range(0,len(articleData)):
         
        text = articleData[i]["content"]
        text = str(text)
        

        text_words = text.split()

        glyph_data_counts = [] #this is our data to build one glyph. Each integer in the list will correspond to num of hits from each wordlist.
        
        for wordlist in wordlists: #for each wordlist

            wordlist_hits = 0
            for search_word in wordlist: #for each word in the wordlist, find any matches in the text, and add them to the total hits for that wordlist

                matches = difflib.get_close_matches(search_word,text_words,n=20,cutoff=0.6)
                # print("there were ",len(matches)," matches. The match was",str(matches),)
                wordlist_hits = wordlist_hits + len(matches)
            
            #END FOR search_word in wordlist
            
            glyph_data_counts.append(wordlist_hits) #appending the hits for each wordlist into the glyph list
        
        #END FOR wordlist in wordlists

        allGlyphData.append(glyph_data_counts)  #appending the glyph list to the antzfile list
        print("Abstract parsed",i+1,"/",len(articleData))
    #END FOR each entry in articleData list of dict

    if search_metadata["scaling_type"] == "minmax":
        # print(search_metadata["scaling_range"])
        scaler = MinMaxScaler(feature_range=search_metadata["scaling_range"])
        scaler.fit(allGlyphData)

    scaledAllGlyphData = scaler.transform(allGlyphData)
    # print('we scaled allGlyphData')
    # print(scaledAllGlyphData)
    
    return scaledAllGlyphData

def generate_centered_grid(N, step=1): # N: integer number of points we want generated| step: float value of x and y distance we want our points to be spaced by

    coordinates = []
    
    # Determine grid dimensions based on N, number of points
    grid_size = math.floor(math.sqrt(N))
    offset = grid_size // 2  # To center the grid around (0, 0)
    
    # Generate coordinates symmetrically around (0,0)
    for i in range(0,grid_size + 1):
        for j in range(0,grid_size + 1):
            x = (i * step) - offset * step
            y = (j * step) - offset * step
            coordinates.append((x, y))
            if len(coordinates) == N:  # Stop when we have N points
                return coordinates
    
    return coordinates

def evenlySpacedAngles(N,objAngle = 360): #N: how many elements we want evenly spaced around 360deg object
    
    step = objAngle/N
    angles = []
    for i in range(0,N):
        
        added_angle = 0 + i * step
        angles.append(added_angle)
    
    return angles #the angles at which our N points exist

def chooseBasicColors(allGlyphData):
    """
    chooseBasicColors Selects the appropriate colors based upon how many glyph branch 2 elements there are. AKA chooses a color for each wordlist

    Args:
        allGlyphData (list of list): list of list containing floats, which scale each glyph element

    Returns:
        (list of list): list containing x entries, which are each a list of 3 integers, representing RGB 0-255 values.
    """
    roygbiv_gradient = [
        [255, 0, 0], [255, 25, 0], [255, 50, 0], [255, 75, 0], [255, 100, 0],  # R -> O
        [255, 125, 0], [255, 150, 0], [255, 175, 0], [255, 200, 0], [255, 225, 0],
        [255, 255, 0], [225, 255, 0], [200, 255, 0], [175, 255, 0], [150, 255, 0],  # O -> Y
        [125, 255, 0], [100, 255, 0], [75, 255, 0], [50, 255, 0], [25, 255, 0],
        [0, 255, 0], [0, 255, 25], [0, 255, 50], [0, 255, 75], [0, 255, 100],  # Y -> G
        [0, 255, 125], [0, 255, 150], [0, 255, 175], [0, 255, 200], [0, 255, 225],
        [0, 255, 255], [0, 225, 255], [0, 200, 255], [0, 175, 255], [0, 150, 255],  # G -> B
        [0, 125, 255], [0, 100, 255], [0, 75, 255], [0, 50, 255], [0, 25, 255],
        [0, 0, 255], [25, 0, 255], [50, 0, 255], [75, 0, 255], [100, 0, 255],   # B transition
        [125, 0, 255], [150, 0, 255], [175, 0, 255], [200, 0, 255], [225, 0, 255],
        [255, 0, 255], [255, 0, 225], [255, 0, 200], [255, 0, 175], [255, 0, 150] #V transition
    ]

    num_colors_needed = len(allGlyphData[0]) #aka # of wordlists
    num_colors_availible = len(roygbiv_gradient)

    indices_ish = evenlySpacedAngles(num_colors_needed,num_colors_availible)

    indices = []
    for i in indices_ish:
        indices.append(int(i))
    
    colors = []
    for index in indices:
        colors.append(roygbiv_gradient[index])
    
    return colors

def generateTitleURLTag(singleArticleData):
    """
    generateTitleURLTag _summary_

    Args:
        singleArticleData (dict): the dictionary contained in a single list entry of articleData. Dict includes article content and metadata

    Returns:
        tag_string_format(str): string in html format that includes the display tag and url to original article.
    """
    
    title = singleArticleData["title"]
    if title == None:
        title = "No Title Parsed"
    url = singleArticleData["url"]

    html_string = '<a href="' + url + '">' + title + '<a>'

    return html_string

def constructBasicGlyphs(allGlyphData,articleData, search_metadata = {
                                            "geometrySelection": "Toroid", 
                                            "wordlist_paths" : ["path/to/WL1.txt","path/to/WL2.txt","path/to/WL3.txt"],
                                            "search_string": "sample string",
                                            "num_results_requested": 200,
                                            "scaling_range": (0.2,2.5),
                                            "scaling_type": "absolute"}): 
    
    
    geometrySelectionDict = {"Toroid":7,
                             "Sphere":3,
                             "Cube":1,
                             "Octahedron":11}

    cwd = os.getcwd()
    
    core_glyph_csv_path = os.path.join(cwd,"resources","glyph_header.csv")
    working_glyph_row_path = os.path.join(cwd,"resources","glyph_layer_2_model_ring.csv")
    first_two_element_of_glyph_path = os.path.join(cwd,"resources","glyph_root_and_layer_1.csv")
    tag_file_path = os.path.join(cwd,"resources","tag_file_header.csv")


    antzfile = pd.read_csv(core_glyph_csv_path)
    tagfile = pd.read_csv(tag_file_path)
    

    num_rings = len(allGlyphData[0]) #check len of a single glyph list. for each index in the list we'll make a ring
    ring_angles = evenlySpacedAngles(num_rings)
    glyphSeparationDistance = 10
    glyphLocations = generate_centered_grid(len(allGlyphData),glyphSeparationDistance) #generate (x,y) coords for each root glyph
    

    colors = chooseBasicColors(allGlyphData)

    node_id_counter = 100  #node ids start at 100 and should increment by 1 for each element
    flag_generating_key_glyph = False
    for i in range(0,len(allGlyphData)+1): #append a glyph for each list in allglyphdata
        
        #generate the key glyph on the last iteration
        if i == len(allGlyphData):
            flag_generating_key_glyph = True

        #start by reading the model structure for root and layer 1 toroid
        working_glyph = pd.read_csv(first_two_element_of_glyph_path)

        #initialize tag header file
        working_root_tags = pd.read_csv(tag_file_path)
        
        #update the node_id, parent_id, and record_id (for tag assosciation) for root node
        node_id_counter = node_id_counter + 1
        working_glyph.loc[working_glyph.index[0],['np_node_id','np_data_id','record_id']] = node_id_counter
        working_glyph.loc[working_glyph.index[0],'parent_id'] = 0 #the parent id for the root is always 0

        #building root node tags. Display the title of the article, and embed the article url to be interacted with
        working_glyph.loc[working_glyph.index[0],'tag_mode'] = 0 #encoded int describes fontsize, color, etc of tag 65536033
        working_root_tags.loc[working_root_tags.index[0],'np_tag_id'] = node_id_counter
        working_root_tags.loc[working_root_tags.index[0],'record_id'] = node_id_counter #associates this tag with the node_id of the correct element

        #update the node_id, parent_id, of toroid
        node_id_counter = node_id_counter + 1
        working_glyph.loc[working_glyph.index[1],['np_node_id','np_data_id','record_id']] = node_id_counter
        working_glyph.loc[working_glyph.index[1],'parent_id'] = node_id_counter - 1 #parent id for layer 1 is root id. aka current id - 1
        node_id_layer2_toroid = node_id_counter #saving node id of layer 1 toroid to access in next for loop
        
        
        # print(flag_generating_key_glyph, "iteration = ",i)
        if flag_generating_key_glyph != True:
            #placing the root glyph on the x-y plane
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_x'] = None
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_x'].astype('float')
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_x'] = glyphLocations[i][0] #selecting rows where parent_id ==0 (root glyph element), and the translate_x column, and writing the corresponding value of glyphLocations,

            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_y'] =None
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_y'].astype('float')
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_y'] = glyphLocations[i][1] #so we add the x,y coord of where we want the glyph
    
            #adding text to root node tags. Display the title of the article, and embed the article url to be interacted with
            working_root_tags.loc[working_root_tags.index[0],'title'] = None
            working_root_tags.loc[working_root_tags.index[0],'title'].astype('str')
            working_root_tags.loc[working_root_tags.index[0],'title'] = generateTitleURLTag(articleData[i])


        if flag_generating_key_glyph == True:
            
            #calculating furthest top and right glyph
            positive_coordinates = [coord for coord in glyphLocations if coord[0] >= 0 and coord[1] >= 0]
        
            max_x = max([coord[0] for coord in positive_coordinates])
            max_y = max([coord[1] for coord in positive_coordinates])
            
           #placing the root glyph on the x-y plane
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_x'] = None
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_x'].astype('float')
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_x'] = max_x + 1.5 * glyphSeparationDistance #selecting rows where parent_id ==0 (root glyph element), and the translate_x column, and writing the corresponding value of glyphLocations,

            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_y'] =None
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_y'].astype('float')
            working_glyph.loc[working_glyph['parent_id'] == 0,'translate_y'] = max_y + 1.5 * glyphSeparationDistance #so we add the x,y coord of where we want the glyph

            #adding text to root key glyph node tag.
            working_root_tags.loc[working_root_tags.index[0],'title'] = None
            working_root_tags.loc[working_root_tags.index[0],'title'].astype('str')
            # working_root_tags.loc[working_root_tags.index[0],'title'] = "str that has visualization metadata"

        tagfile = pd.concat([tagfile,working_root_tags])

        for j in range(0,num_rings): #construct a ring in our glyph for each element in scaling data
            
            #add node_id, parent_id, and tag id to the working row
            working_row = pd.read_csv(working_glyph_row_path)
            node_id_counter = node_id_counter + 1
            working_row.loc[working_row.index[0],['np_node_id','np_data_id','record_id']] = node_id_counter
            working_row.loc[working_glyph.index[0],'parent_id'] = node_id_layer2_toroid
            
            #add location of the level 2 toroid on level 1 toroid
            working_row.loc[working_row.index[0],'translate_x'] = None
            working_row.loc[working_row.index[0],'translate_x'].astype(float)
            working_row.loc[working_row.index[0],'translate_x'] = ring_angles[j]
            working_row.loc[working_row.index[0],'translate_z'] = 120

            
            
            #adding color to ring
           
            working_row.loc[working_row.index[0],["color_r","color_g","color_b"]] = colors[j]
            

            #changing data glyph element to be the user-defined geometry
            working_row.loc[working_row.index[0],'np_geometry_id'] = geometrySelectionDict[search_metadata["geometrySelection"]]
            
            if flag_generating_key_glyph == False:

                #scaling toroid in x, y and z directions based on data within allGlyphData
                working_row.loc[working_row.index[0],["scale_x","scale_y","scale_z"]] = None #[i][j] is the i'th glyph in list, and j'th toroid's scale factor
                working_row.loc[working_row.index[0],["scale_x","scale_y","scale_z"]].astype('float')
                working_row.loc[working_row.index[0],["scale_x","scale_y","scale_z"]] = allGlyphData[i][j]
            
            
            if flag_generating_key_glyph == True:
        
                # set default scaling
                working_row.loc[working_row.index[0],["scale_x","scale_y","scale_z"]] = search_metadata["scaling_range"][1]
                
                #building key glyph layer_2 (leaf) tags. Display names of each wordlist that was used to scale that glyph element
                working_leaf_tags = pd.read_csv(tag_file_path)
                working_row.loc[working_row.index[0],'tag_mode'] = 0 #encoded int describes fontsize, color, etc of tag 65536033
                working_leaf_tags.loc[working_leaf_tags.index[0],'np_tag_id'] = node_id_counter
                working_leaf_tags.loc[working_leaf_tags.index[0],'record_id'] = node_id_counter #associates this tag with the node_id of the correct element
                
                tag_string = '<a href="' + search_metadata["wordlist_paths"][j] + '">' + os.path.basename(search_metadata["wordlist_paths"][j]) + '<a>'
                
                working_leaf_tags.loc[working_leaf_tags.index[0],'title'] = None
                working_leaf_tags.loc[working_leaf_tags.index[0],'title'].astype('str')
                working_leaf_tags.loc[working_leaf_tags.index[0],'title'] = tag_string
                tagfile = pd.concat([tagfile,working_leaf_tags])

            #appending working_row to working_glyph
            working_glyph = pd.concat([working_glyph,working_row])

            # END FOR

        
        #appending working_glyph to antzfile
        antzfile = pd.concat([antzfile,working_glyph])
        print("Constructed Glyph ", i+1,"/",len(allGlyphData))
        if flag_generating_key_glyph == True:
            print("Key Glyph Generated in Top Right Corner")


    return antzfile,tagfile


# glyphlocations = generate_centered_grid(50,10)
