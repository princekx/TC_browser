import bokeh
from bokeh.io import curdoc, output_file, show
from bokeh.layouts import row, column, widgetbox
import bokeh.models as bokeh_models
from bokeh.models.widgets import Button
#from bokeh.models import ColumnDataSource
# import ColumnDataSource, DataRange1d, Select
# from bokeh.palettes import Blues4
from bokeh.plotting import figure, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, Range1d, PanTool, WheelZoomTool, BoxSelectTool
)
import iris
import numpy as np
import cf_units as unit
import os, sys
import itertools

def read_info_for_storm_names(f, storm_name):
    names = f.extract('Storm name')[0]
    number = f.extract('Storm serial number')[0]
    tcnames = []
    for n in range(len(names.data)):
        tcnames.append(''.join(names.data[n]) + '_' + ''.join(number.data[n]))
    # years = f.extract('Year based on season')[0]
    jday = f.extract('Modified Julian Day')[0]
    nobs = f.extract('Number of observations for the storm')[0]
    lats = f.extract('Latitude for mapping purposes only')[0]
    lons = f.extract('Longitude for mapping purposes only')[0]
    ind = np.where(np.array(tcnames) == storm_name)[0]
    xlons = lons.data[ind, :nobs.data[ind]][0]
    xlons = np.where(xlons <= 0, xlons + 360, xlons)
    xlats = lats.data[ind, :nobs.data[ind]][0]
    
    jday = jday[ind, :nobs.data[ind]][0]
    time = unit.num2date(jday.data, str(jday.units), unit.CALENDAR_STANDARD)
    time_string = [str(t) for t in time]
    
    #TC names repeated as many times as the lat/lon points for hover tool
    name = ''.join(names.data[ind][0])
    name_repeat_array = [name for i in range(len(xlons))]
    
    storm_info = {}
    storm_info['lons'] = xlons
    storm_info['lats'] = xlats
    storm_info['time'] = time_string
    storm_info['name'] = name_repeat_array
    return storm_info

def read_yearly_storm_names(f, year):
    names = f.extract('Storm name')[0]
    number = f.extract('Storm serial number')[0]
    years = f.extract('Year based on season')[0]
    inds = np.where(years.data == year)[0]
    tcnames = []
    for ind in inds:
        tcnames.append(''.join(names.data[ind]) + '_' + ''.join(number.data[ind]).rstrip())
    return tcnames
def read_storm_years(f):
    year = f.extract('Year based on season')[0]
    return np.unique(year.data)

def update_plot(storm_names_global_list_to_plot):
    #print storm_select.active
    #Storm_names_options.Data
    #print storm_select.labels
    #for st in storm_select.active:
    #    print options_source.data.values()[st]
    
    storm_names_to_plot = [storm_select.labels[i] for i in storm_select.active]
    print storm_names_to_plot
    # Update the global list by selection
    storm_names_global_list_to_plot.extend(storm_names_to_plot)
    print storm_names_global_list_to_plot
    
    storm_names_global_list_to_plot = np.unique(storm_names_global_list_to_plot)
    
    plot = figure(plot_width=800, \
                  tools=["pan,reset,save,wheel_zoom"])  # , toolbar_location=None)
    for storm in storm_names_global_list_to_plot:
        storms_info_data = read_info_for_storm_names(f, storm)
        # make the bokeh source object
        # Make Bokeh data object
        source = bokeh_models.ColumnDataSource(data=storms_info_data)
        
        
        plot.line('lons', 'lats', source=source, line_width=3, line_alpha=0.6)#, line_color = colors[i])
        plot.circle('lons', 'lats', source=source)
        
    hover = bokeh_models.HoverTool(tooltips=[("Name", "@name"),\
                                             ("Coord", "(@lons, @lats)"),\
                                             ("Time", "@time"),\
                                             ])
    plot.add_tools(hover)
    # # fixed attributes
    plot.title.text = "Tropical cyclone " + selected_storm + " " + selected_year
    plot.xaxis.axis_label = 'Longitude'
    plot.yaxis.axis_label = "Latitude"
    plot.axis.axis_label_text_font_style = "bold"
    # plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.3

# Set up callbacks
def update_storm_names(attrname, old, new):
    year = year_select.value
    Data = read_yearly_storms(int(year))
    Storm_names_options = [Data[n]['TCName'] for n in range(len(Data))]
    # plot.title.text = text.value
# In[60]:


#datadir = '/home/prince/Dropbox/WCSSP_SEA/Philippines/'
datadir = '/project/MJO_GCSS/SoutheastAsia_data/CYCLONES'
f = iris.load(os.path.join(datadir, 'Basin.WP.ibtracs_all.v03r09.nc'))
# get menu options as years
unique_years = read_storm_years(f)
year_options = [str(x) for x in unique_years]
year_options.sort(reverse=True)

# select a year to start the menu
selected_year = year_options[0]
menu_data = {}
# get storm names for the selected year
tcnames = read_yearly_storm_names(f, int(selected_year))
menu_data[selected_year] = tcnames
# select the first storm to start the menu
selected_storm = tcnames[0]

storm_names_global_list_to_plot = []
# make the bokeh source object
options_source = bokeh_models.ColumnDataSource(data=menu_data)
# get the lat lon of the selected storm
storms_info_data = read_info_for_storm_names(f, selected_storm)

# Make Bokeh data object
source = bokeh_models.ColumnDataSource(data=storms_info_data)
#print storms_info_data
# hover = bokeh_models.HoverTool(tooltips=[
#     ("Name", "@name"),
#     ("Coord", "(@lons, @lats)"),
#     ("Time", "@time"),
#     ])

#colors = bokeh.palettes.Category20
#colors = list(itertools.chain(*colors.values()))

map_options = bokeh_models.GMapOptions(lat=11., lng=122., map_type="roadmap", zoom=4)

plot = bokeh_models.GMapPlot(x_range=bokeh_models.Range1d(), \
                             y_range=bokeh_models.Range1d(), \
                             map_options=map_options, \
                             plot_width=800, plot_height=600)
plot.api_key = "AIzaSyCzb3UKR3aAcuiUhRZlTQU_rBgIMUKI_Dw"

#plot = figure(plot_width=800, \
#                  tools=["pan,reset,save,wheel_zoom"])  # , toolbar_location=None)
#plot.line('lons', 'lats', source=source, line_width=3, line_alpha=0.6)#, line_color = colors[i])
#plot.circle('lons', 'lats', source=source)

circle = bokeh_models.Circle(x="lons", y="lats", size=5, fill_color="blue", fill_alpha=0.8, line_color=None)
line = bokeh_models.Line(x="lons", y="lats", line_width=3, line_color="blue")
plot.add_glyph(source, line)
plot.add_glyph(source, circle)

hover = bokeh_models.HoverTool(tooltips=[("Name", "@name"),\
                                         ("Coord", "(@lons, @lats)"),\
                                         ("Time", "@time"),\
                                         ])
plot.add_tools(hover)
plot.add_tools(bokeh_models.PanTool(), bokeh_models.WheelZoomTool(), bokeh_models.BoxSelectTool())
# # fixed attributes
plot.title.text = "Tropical cyclone " + selected_storm + " " + selected_year
plot.xaxis.axis_label = 'Longitude'
plot.yaxis.axis_label = "Latitude"
plot.axis.axis_label_text_font_style = "bold"
# plot.x_range = DataRange1d(range_padding=0.0)
plot.grid.grid_line_alpha = 0.3


year_select = bokeh_models.Select(value=selected_year, title='Year:', \
                                  options=year_options)
storm_select = bokeh_models.CheckboxGroup(labels=menu_data[selected_year], \
                                          active=[0], width=100)
select_all_button = bokeh_models.Button(label="Select all")
clear_all_button = bokeh_models.Button(label="Clear")
plot_update_button = bokeh_models.Button(label="Update plot")
#value=selected_storm, title='Storm:', \
#options=options_source.data[selected_year])

def update_storm_names(attrname, old, new):
    # Get the current slider values   
    tcnames = read_yearly_storm_names(f, int(year_select.value))
    options_source.data = {year_select.value:tcnames}
    #print options_source.data.values()[0]
    storm_select.labels = tcnames

def update_selection():
    storm_select.active = list(range(len(menu_data[selected_year])))
def clear_selection():
    storm_select.active = list([])

# #
year_select.on_change('value', update_storm_names)
select_all_button.on_click(update_selection)
clear_all_button.on_click(clear_selection)
plot_update_button.on_click(update_plot(storm_names_global_list_to_plot))

#storm_select.on_change('value', update_plot)
controls = column(year_select)
#select_clear_buttons = row(select_all_button, clear_all_button)

group = widgetbox(select_all_button, clear_all_button, storm_select)
#plot_group = widgetbox(plot_update_button, plot)
# show(row(plot, controls))

curdoc().add_root(row(column(controls, group), column(plot_update_button, plot)))
curdoc().title = "Weather"
#output_file("gmap_plot.html")
#show(plot)
