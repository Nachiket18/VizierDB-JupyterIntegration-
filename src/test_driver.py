
import nbformat as nb 
import ast
import os
from collections import deque,defaultdict
from parse_notebook import parse_notebook
from itertools import groupby
import matplotlib.pyplot as plt
import pickle



def main():

    input_dir = '/home/nachiket/python_data_notebooks/extracted_python/final_notebooks_dataset/'

    output_cells_parallelism_total_cells = []
    output_cells_parallelism_max_depth = []


    for file in os.listdir(input_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".ipynb") and filename in ( 'script221.ipynb' ): #,'5_Pandas.ipynb','04-representing-data-feature-engineering.ipynb' , 'ch08.005.2D.Stress.Transform.ipynb','ConcurrencyAndCoroutines.ipynb','eCar_Case-Team-7.ipynb','script221.ipynb','script719.ipynb','script930.ipynb','script1104.ipynb','translate-pytorch.ipynb'):
            f_name = input_dir + '' + filename
            
            try:
                
                out = nb.read(f_name,as_version=4)

                max_depth,total_cells = parse_notebook.parse_notebook_test(out)
                
                print(max_depth,total_cells)

                if total_cells > 60 and total_cells <= 90:
                    print(f_name)
                    print(total_cells)
                    print(max_depth)

                output_cells_parallelism_total_cells.append(total_cells)
                output_cells_parallelism_max_depth.append(max_depth)

                input_provenance,output_provenance = parse_notebook.parse_notebook(out)
                print(input_provenance,output_provenance)

                #print(parse_notebook.display_input_provenance())
            
            except:
                pass

    x_values = [1,5,10,15,20,50,70,100,120,140,160,180,200,220,250]
    y_values = [1,2,3,4,5,10,15,20]

    plt.scatter(output_cells_parallelism_total_cells,output_cells_parallelism_max_depth,alpha=0.5)
    plt.title('Parallelism metric')
    plt.xlabel('Total Cells in Notebook')
    plt.ylabel('Depth - Max length intercell dependency')
    plt.axis([0,150,0,25])
    plt.savefig('output.png')       


if __name__ == '__main__':
    main() 