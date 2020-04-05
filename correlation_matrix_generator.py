##########################################################
# Author: Raghav Sikaria
# LinkedIn: https://www.linkedin.com/in/raghavsikaria/
# Github: https://github.com/thepirhana
# Last Update: 5-4-2020
# Project: Visualise a correlation matrix with User
#           intercativity features
##########################################################

## ALL IMPORTS
import fileinput
from math import pi
import pandas as pd
from bokeh.io import show, output_notebook,output_file
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter, Select, ColumnDataSource
from bokeh.plotting import figure,curdoc,save
from bokeh.sampledata.unemployment1948 import data
from bokeh.layouts import column, layout, widgetbox
from bokeh.models.callbacks import CustomJS
from bokeh.palettes import inferno, magma, viridis, gray, cividis, turbo
from bokeh import events

OUTPUT_FILE = 'correlation_matrix.html'
BOKEH_API_CDN = '<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-1.4.0.js"></script>'
BOKEH_TOOLS = "hover,save,pan,reset,wheel_zoom,box_select,tap,undo,redo,zoom_in,zoom_out,crosshair"
output_file(OUTPUT_FILE)

def get_reversed_list(list_object):
    ## UTILITY FUNCTION TO REVERSE A COLOR PALETTE LIST
    list_object.reverse()
    return list_object

def carry_bokeh_correction():
    ## GETTING AROUND BOKEH - SWITCHING FROM MIN TO MAIN (BASED ON RECOMMENDATIONS ON SIMLILAR QUESTIONS)
    ##                      - ADDING BOKEH API CDN SINCE BOKEH MISSES IT BYDEFAULT (KNOWN ISSUE)
    with fileinput.FileInput(OUTPUT_FILE, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('1.4.0.min', '1.4.0'), end='')

    with open(OUTPUT_FILE) as f:
        code = f.readlines() 

    new_code = []
    for line in code:
        new_code.append(line)
        if 'bokeh-widgets-1.4.0' in line:
            new_code.append(BOKEH_API_CDN)

    with open(OUTPUT_FILE,'w') as f:
        f.writelines(new_code)

def generate_correlation_graph(correlation_matrix_csv_path, title='Correlation Matrix',plot_height=1000, plot_width=1600):
    ## PREPARING CORRELATION MATRIX
    df = pd.read_csv(correlation_matrix_csv_path)
    df = df.set_index('Unnamed: 0').rename_axis('parameters', axis=1)
    df.index.name = 'level_0'

    ## AXIS LABELS FOR PLOT
    common_axes_val = list(df.index)
    df = pd.DataFrame(df.stack(), columns=['correlation']).reset_index()
    source = ColumnDataSource(df)

    ## FINDING LOWEST AND HIGHEST OF CORRELATION VALUES
    low_df_corr_min = df.correlation.min()
    high_df_corr_min = df.correlation.max()
    no_of_colors = len(df.correlation.unique())

    ### PLOT PARTICULARS
    ## CHOOSING DEFAULT COLORS
    mapper = LinearColorMapper(palette=get_reversed_list(cividis(no_of_colors)), low=low_df_corr_min, high=high_df_corr_min)

    ## SETTING UP THE PLOT
    p = figure(title=title,x_range=common_axes_val, y_range=list((common_axes_val)),x_axis_location="below", plot_width=plot_width, plot_height=plot_height,tools=BOKEH_TOOLS, toolbar_location='above',tooltips=[('Parameters', '@level_0 - @parameters'), ('Correlation', '@correlation')])
    p.toolbar.autohide = True

    ## SETTING UP PLOT PROPERTIES
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "12pt"
    p.xaxis.major_label_orientation = pi/2

    ## SETTING UP HEATMAP RECTANGLES
    cir = p.rect(x="level_0", y="parameters", width=1, height=1,source=source,fill_color={'field': 'correlation', 'transform': mapper},line_color=None)

    ## SETTING UP COLOR BAR
    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",ticker=BasicTicker(desired_num_ticks=10),formatter=PrintfTickFormatter(format="%.1f"),label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    ## AVAILABLE COLOR SCHEMES
    COLOR_SCHEME = {
        'Cividis':get_reversed_list(cividis(no_of_colors)),
        'Gray':get_reversed_list(gray(no_of_colors)),
        'Inferno':get_reversed_list(inferno(no_of_colors)),
        'Magma':get_reversed_list(magma(no_of_colors)),
        'Viridis':get_reversed_list(viridis(no_of_colors)),
        'Turbo':get_reversed_list(turbo(no_of_colors)),
    }

    ## JS CALLBACK
    callback = CustomJS(args=dict(col_sch=COLOR_SCHEME,low=low_df_corr_min,high=high_df_corr_min,cir=cir,color_bar=color_bar), code="""
    // JavaScript code goes here
    var chosen_color = cb_obj.value;
    var color_mapper = new Bokeh.LinearColorMapper({palette:col_sch[chosen_color], low:low, high:high});
    cir.glyph.fill_color = {field: 'correlation', transform: color_mapper};
    color_bar.color_mapper.low = low;
    color_bar.color_mapper.high = high;
    color_bar.color_mapper.palette = col_sch[chosen_color];
    """)

    ## SELECT OPTION FOR INTERACTIVITY GIVEN TO USER
    select = Select(title='Color Palette',value='cividis', options=list(COLOR_SCHEME.keys()), width=200, height=50)

    ## CALL BACK TO BE TRIGGERED WHENEVER USER SELECTS A COLOR PALETTE
    select.js_on_change('value', callback)

    ## GENERATION FINAL PLOT BY BINDING PLOT AND SELECT OPTION
    final_plot = layout([[select],[p]])
    curdoc().add_root(final_plot)
    save(final_plot)

if __name__ == "__main__": 
    generate_correlation_graph('wine_correlation.csv')
    carry_bokeh_correction()