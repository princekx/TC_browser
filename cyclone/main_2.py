import bokeh
from bokeh.io import curdoc
from bokeh.layouts import row, column
import bokeh.models as bokeh_models

#from bokeh.models import ColumnDataSource
# import ColumnDataSource, DataRange1d, Select
# from bokeh.palettes import Blues4
from bokeh.plotting import figure, show

import iris
import numpy as np
import cf_units as unit
import os, sys

def read_info_for_storm_names(f, year, storm_name):
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
    name = ''.join(names.data[ind,:nobs.data[ind]][0])
    name_repeat_array = [name for i in range(len(xlons))]
    
    storm_info = {}
    storm_info['lons'] = list(xlons)
    storm_info['lats'] = list(xlats)
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

def update_plot(attrname, old, new):
    storms_info_data = read_info_for_storm_names(f, \
                                                year_select.value, \
                                                storm_select.value)
    # make the bokeh source object
    # Make Bokeh data object
    print storms_info_data
    source = bokeh_models.ColumnDataSource(data=storms_info_data)
    plot.title.text = "Tropical cyclone " + storm_select.value + " " + year_select.value
    plot.line('lons', 'lats', source=source, line_width=3, line_alpha=0.6)
    plot.circle('lons', 'lats', source=source, radius = 0.15)
    
# Set up callbacks
def update_storm_names(attrname, old, new):
    year = year_select.value
    Data = read_yearly_storms(int(year))
    Storm_names_options = [Data[n]['TCName'] for n in range(len(Data))]
    # plot.title.text = text.value
def update_storm_names(attrname, old, new):
    # Get the current slider values   
    tcnames = read_yearly_storm_names(f, int(year_select.value))
    options_source.data = {year_select.value:tcnames}
    print options_source.data.values()[0]
    storm_select.options = tcnames
    
# In[60]:


#datadir = '/home/prince/Dropbox/WCSSP_SEA/Philippines/'
datadir = '/project/MJO_GCSS/SoutheastAsia_data/CYCLONES/'
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


# make the bokeh source object
options_source = bokeh_models.ColumnDataSource(data=menu_data)
# get the lat lon of the selected storm
storms_info_data = read_info_for_storm_names(f, selected_year, selected_storm)

# Make Bokeh data object
source = bokeh_models.ColumnDataSource(data=storms_info_data)
print storms_info_data
hover = bokeh_models.HoverTool(tooltips=[
    ("Name", "@name"),
    ("Time", "@time"),
    ("(lon,lat)", "(@lons, @lats)"),
    ])
i = 0

#colors = bokeh.palettes.Category20
#colors = list(itertools.chain(*colors.values()))

plot = figure(plot_width=800, \
                  tools=["pan,reset,save,wheel_zoom", hover])  # , toolbar_location=None)
plot.line('lons', 'lats', source=source, line_width=3, line_alpha=0.6)#, line_color = colors[i])
plot.circle('lons', 'lats', source=source, radius = 0.15)
# # fixed attributes
plot.title.text = "Tropical cyclone " + selected_storm + " " + selected_year
plot.xaxis.axis_label = 'Longitude'
plot.yaxis.axis_label = "Latitude"
plot.axis.axis_label_text_font_style = "bold"
# plot.x_range = DataRange1d(range_padding=0.0)
plot.grid.grid_line_alpha = 0.3


year_select = bokeh_models.Select(value=selected_year, title='Year:', \
                                  options=year_options)
storm_select = bokeh_models.Select(value=selected_storm, title='Storm:', \
                                   options=options_source.data[selected_year])



# #
year_select.on_change('value', update_storm_names)
storm_select.on_change('value', update_plot)
controls = column(year_select, storm_select)

# show(row(plot, controls))

curdoc().add_root(row(plot, controls))
curdoc().title = "Weather"

