import streamlit as st
import pandas as pd
import nivo
import data
import streamlit_elements

logger = st.session_state['logger']

def stops_uof_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time_stats, selected_time_series, selected_gender, selected_residency, 
                            selected_scale,
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    _, summary_data = data.get_summary_stats(police_data, population, selected_reason, selected_time_stats, selected_gender, selected_residency)
    time_data = data.get_timelines(police_data, population, selected_reason, selected_time_series, selected_gender, 
                                   selected_residency, selected_scale)
    
    min_date, max_date = data.get_date_range(selected_time_stats, data=police_data, residency=selected_residency)
    min_date = max(min_date, pd.Period('2021-07'))
    date_range = f"{min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}"

    no_data = min_date > max_date

    if not no_data:
        with streamlit_elements.elements('stops_uof'):
            nivo.bar(summary_data['Officer UoF Counts'],
                    title=f"Use of Force By Officer: {date_range}", stacked=True, ylabel="Subject Race",
                    columns=selected_races, layout='horizontal',_debug=_debug,
                    yoffset=-150)
            nivo.bar(summary_data['Subject UoF Counts'],
                    title=f"Use of Force By Subject: {date_range}", stacked=True, ylabel="Subject Race",
                    columns=selected_races, layout='horizontal',_debug=_debug,
                    yoffset=-150)
            nivo.bar(summary_data['UoF Rates'],
                    title=f"Use of Force Rates: {date_range}", stacked=False,
                    columns=selected_races, layout='vertical',_debug=_debug, label_format=[".1%",".0%"])
    else:
        st.warning(f"Use of force data was not collected prior to {pd.Period('2021-07').strftime('%B %Y')} so some charts cannot be displayed.")
            
    with streamlit_elements.elements('stops_uof_time'):
        nivo.plot(time_data['UoF Rate']["Officer"], ylabel="Use of Force Rate", time_scale=selected_scale, 
                title=r"Officer Use of Force Rate: % of stops that end in an officer using force",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])
        nivo.plot(time_data['UoF Rate']["Subject"], ylabel="Use of Force Rate", time_scale=selected_scale, 
                title=r"Subject Use of Force Rate: % of stops that end in a subject using force",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])
    
    if not no_data:
      selectedUoF = st.selectbox("Use of Force", summary_data['Uof Outcomes'].keys())
      for k in ['use of force type']:
        v = selectedUoF
        if k in st.session_state and st.session_state[k]!=v:
            logger.info(f"Value of filter {k} changed to {v}")
    
        st.session_state[k] = v
      with streamlit_elements.elements('stops_uof2'):
          nivo.bar(summary_data['Uof Outcomes'][selectedUoF],
                  title=f"Outcomes of Stops Where Use of Force Occurs: {date_range}", stacked=True, ylabel="Subject Race",
                  columns=selected_races, layout='horizontal',_debug=_debug, percent=True,
                  yoffset=-150)