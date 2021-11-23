paramDict = {
    "Augsburg": {
        "bounding_box": [10.763362,48.249337,10.959333,48.468336],
        "centroid": [48.354761,10.896351],
        "small_buf_default": 2.25,          # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.5            # medium-sized city (< 1 Mio. inhabitants)
    },
    "Dresden": {
        "bounding_box": [13.1956,50.8285,14.2901,51.2662],
        "centroid": [51.05,13.73],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Düsseldorf": {
        "bounding_box": [6.61712,51.148577,6.949457,51.3066],
        "centroid": [51.23,6.78],
        "small_buf_default": 2,             # medium-sized city  (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city  (< 1 Mio. inhabitants)
    },
    "Bern": {
        "bounding_box": [7.423641,46.93916,7.469955,46.962112],
        "centroid": [46.945876,7.415994],
        "small_buf_default": 2,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25           # small-sized city (< 200k inhabitants)
    },  
    "Pforzheim": {
        "bounding_box": [8.653482,48.873994,8.743249,48.910329],
        "centroid": [48.877046,8.710584],
        "small_buf_default": 2,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25           # small-sized city (< 200k inhabitants)
    },
    "Wuppertal": {
        "bounding_box": [7.014072,51.165803,7.31343,51.318062],
        "centroid": [51.240631,7.163216],
        "small_buf_default": 2,             # medium-sized city  (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city  (< 1 Mio. inhabitants)
    },
    "Stuttgart": {  # Region Stuttgart
        "bounding_box": [8.772582,48.511551,9.976016,49.070801],
        "centroid": [48.775556,9.182778],
        "small_buf_default": 2.25,          # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.5            # medium-sized city (< 1 Mio. inhabitants)
    },
    # FOR TESTING ONLY, NOT AN ACTUAL REGION
    "wedding": {
        "bounding_box": [13.319638,52.538373,13.382339,52.570332],
        "centroid": [52.555071, 13.349667],
        "small_buf_default": 2.5,            # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75            # large-sized city (> 1 Mio. inhabitants)
    },
    "Hannover": {
        "bounding_box": [9.60443,52.305137,9.918426,52.454335],
        "centroid": [52.3796, 9.7617],
        "small_buf_default": 2,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city (< 1 Mio. inhabitants)
    },
    "Leipzig": {
        "bounding_box": [12.344361,51.329879,12.408767,51.357489],
        "centroid": [51.3403333, 12.37475],
        "small_buf_default": 2,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city (< 1 Mio. inhabitants)
    },
    "Konstanz": {
        "bounding_box": [8.989582,47.635771,9.290482,47.762737],
        "centroid": [47.669167, 9.177778],
        "small_buf_default": 2,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25           # small-sized city (< 200k inhabitants)
    },
    "Nuernberg": {  # Nürnberg/Erlangen/Fürth
        "bounding_box": [10.826157, 49.301248, 11.310743, 49.639198],
        "centroid": [49.455556,11.078611],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Mannheim": {  # Mannheim/Ludwigshafen/Heidelberg
        "bounding_box": [8.183910, 49.315638, 8.721256, 49.591742],
        "centroid": [49.48776,8.46622],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Friedrichshafen": {
        "bounding_box": [9.376298, 47.636371, 9.578991, 47.741530],
        "centroid": [47.654167,9.479167],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Lindau": {
        "bounding_box": [9.625018, 47.529972, 9.747052, 47.616354],
        "centroid": [47.545833,9.683889],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Karlsruhe": {  # Karlsruhe/Ettlingen
        "bounding_box": [8.239066, 48.920325, 8.561666, 49.099789],
        "centroid": [49.014,8.4043],
        "small_buf_default": 2,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city (< 1 Mio. inhabitants)
    },
    "Freiburg": {  # Freiburg (Breisgau)
        "bounding_box": [7.654762, 47.896378, 7.937174, 48.079058],
        "centroid": [47.994828,7.849881],
        "small_buf_default": 2,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city (< 1 Mio. inhabitants)
    },
    "Tübingen": {  # Landkreis Tübingen
        "bounding_box": [8.762020, 48.368017, 9.177162, 48.625407],
        "centroid": [48.519410, 9.057887],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Mainz": {  # Mainz/Wiesbaden
        "bounding_box": [8.134421, 49.891550, 8.337525, 50.129153],
        "centroid": [50.008622, 8.256472],
        "small_buf_default": 2,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city (< 1 Mio. inhabitants)
    },
    "Rastatt": {  # Rastatt/Baden Baden
        "bounding_box": [8.084772, 48.663558, 8.299544, 48.886542],
        "centroid": [48.803716, 8.219837],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Kaiserslautern": {  # Kaiserslautern
        "bounding_box": [7.596432, 49.342713, 7.926639, 49.506781],
        "centroid": [49.444722, 7.768889],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Darmstadt": {  # Darmstadt
        "bounding_box": [8.482112,49.787748,8.814449,49.959337],
        "centroid": [49.87,8.65],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Saarbrücken": {  # Saarbrücken
        "bounding_box": [6.856136,49.148703,7.136287,49.32087],
        "centroid": [49.23,6.99],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Weimar": {  # Weimar
        "bounding_box": [11.249637,50.949992,11.395549,51.029304],
        "centroid": [50.98,11.32],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Brühl": {  # Brühl
        "bounding_box": [6.864489,50.805607,6.936215,50.857649],
        "centroid": [50.83,6.9],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Ulm": {  # Ulm
        "bounding_box": [9.861932,48.312447,10.126978,48.481816],
        "centroid": [48.40,9.99],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Sigmaringen": {  # Sigmaringen
        "bounding_box": [9.06096,47.992125,9.375444,48.18053],
        "centroid": [48.09,9.21],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Saarlouis": {  # Landkreis Saarlouis
        "bounding_box": [6.483765, 49.198789, 7.027267, 49.522844],
        "centroid": [49.316937, 6.751789],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Landau": {  # Landau (Pfalz)
        "bounding_box": [7.977261, 49.140156, 8.193764, 49.249082],
        "centroid": [49.196232, 8.113476],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Frankfurt": {  # Frankfurt/Offenbach/Hanau
        "bounding_box": [8.421933, 49.973915, 9.050441, 50.266730],
        "centroid": [50.106528, 8.686167],
        "small_buf_default": 2,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city (< 1 Mio. inhabitants)
    },
    "Bruchsal": {  # Bruchsal
        "bounding_box": [8.489138, 49.061912, 8.734475, 49.188278],
        "centroid": [49.125645, 8.589541],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Breisgau-Hochschwarzwald": {  # Landkreis Breisgau-Hochschwarzwald
        "bounding_box": [7.495586, 47.717743, 8.445949, 48.155544],
        "centroid": [47.881980, 7.744397],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Alzey": {  # Alzey/Worms
        "bounding_box": [7.813212, 49.553022, 8.493923, 49.937815],
        "centroid": [49.739247, 8.134097],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Koblenz": {  # Koblenz
        "bounding_box": [7.422792, 50.262767, 7.726128, 50.429590],
        "centroid": [50.354275, 7.588423],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Odenwald": {  # Odenwaldkreis
        "bounding_box": [8.702550, 49.443672, 9.220281, 49.880131],
        "centroid": [49.670379, 8.980350],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Ortenau": {  # Ortenaukreis
        "bounding_box": [7.561501, 48.151376, 8.342251, 48.740415],
        "centroid": [48.469280, 7.948020],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Vulkaneifel": {  # Landkreis Vulkaneifel
        "bounding_box": [6.313098, 50.045198, 7.091610, 50.431860],
        "centroid": [50.220587, 6.660884],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Wetterau": {  # Wetteraukreis
        "bounding_box": [8.480659, 50.157677, 9.341713, 50.528400],
        "centroid": [50.339471, 8.754113],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Trier": {  # Trier
        "bounding_box": [6.499611, 49.674169, 6.785407, 49.874362],
        "centroid": [49.7596, 6.6439],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Tuttlingen": {  # Landkreis Tuttlingen
        "bounding_box": [8.543100, 47.827349, 9.058461, 48.227543],
        "centroid": [47.985494, 8.819951],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "München": {  # München
        "bounding_box": [11.345589, 48.045297, 11.797402, 48.239568],
        "centroid": [48.13, 11.57],
        "small_buf_default": 2.5,            # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75            # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244,51.346258,7.537335,51.645947],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet1": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244,51.346258,7.0808675,51.4961025],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet11": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244000,51.3462580,6.8526337,51.4211802],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet12": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.8526337,51.3462580,7.0808675,51.4211802],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet13": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.0808675,51.3462580,7.3091012,51.4211802],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet14": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.3091012,51.3462580,7.5373350,51.4211802],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet2": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244,51.4961025,7.0808675,51.645947],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet21": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244000,51.4211802,6.8526337,51.4961025],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet22": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.8526337,51.4211802,7.0808675,51.4961025],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet23": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.0808675,51.4211802,7.3091012,51.4961025],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet24": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.3091012,51.4211802,7.5373350,51.4961025],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet3": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.0808675,51.346258,7.537335,51.4961025],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet31": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244000,51.4961025,6.8526337,51.5710247],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet32": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.8526337,51.4961025,7.0808675,51.5710247],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet33": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.0808675,51.4961025,7.3091012,51.5710247],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet34": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.3091012,51.4961025,7.5373350,51.5710247],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet4": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.0808675,51.4961025,7.537335,51.645947],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet41": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.6244000,51.5710247,6.8526337,51.6459470],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet42": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [6.8526337,51.5710247,7.0808675,51.6459470],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet43": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.0808675,51.5710247,7.3091012,51.6459470],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Ruhrgebiet44": {  # Ruhrgebiet
        #"bounding_box": [6.4913, 51.2998, 7.9004, 51.7517],
        "bounding_box": [7.3091012,51.5710247,7.5373350,51.6459470],
        "centroid": [51.51, 7.18],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    },
    "Eichwalde": {  # Landkreis Tuttlingen
        "bounding_box": [13.553875, 52.326109, 13.674421, 52.397836],
        "centroid": [52.36261, 13.61594],
        "small_buf_default": 2,  # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25  # small-sized city (< 200k inhabitants)
    },
    "Bielefeld": {
        "bounding_box": [8.349841, 51.9205, 8.715136, 52.099701],
        "centroid": [52.022445, 8.532489],
        "small_buf_default": 2,  # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.25  # medium-sized city (< 1 Mio. inhabitants)
    },
    "Berlin": {
        "bounding_box": [12.9731, 52.3452, 13.8298, 52.6941],
        "centroid": [52.51, 13.40],
        "small_buf_default": 2.5,  # large city (>1 Mio. inhabitants)
        "large_buf_default": 2.75  # large-sized city (> 1 Mio. inhabitants)
    }
}
