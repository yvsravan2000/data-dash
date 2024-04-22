# Import packages and modules | External
import warnings
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

# Import packages and modules | Internal
from validata_package import config as cfg

# Streamlit page content function
def showPageContent() -> None:
    # Display page title
    colored_header(
        label="Home",
        description="",
        color_name="gray-70",
    )

    # Show content
    st.write("Information bla bla...")

# Streamlit sidebar function
def showSidebarContent() -> None:
    # Display sidebar title
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "🔍 Validata";
                display: block;
                padding: 20px;
                padding-top: 40px;
                font-size: 28px;
                font-weight: bold;
                position: static;
                margin-right: 6px;
                margin-bottom: -60px;
                backdrop-filter: blur(100px);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display version details (MAJOR.MINOR.PATCH-IDENTIFIER)
    st.sidebar.info(f"App version: {cfg.app_version}")

    # Display maintainance details if not empty
    if(cfg.maintainance_message!=""):
        st.sidebar.warning(f"Maintainance update: -\n\n{cfg.maintainance_message}")

# Streamlit page function
def homePage() -> None:
    # Set-up streamlit page configuration
    st.set_page_config(
        page_title = "Validata: Home",
        page_icon = ":mag:",
        layout = "wide",
        initial_sidebar_state = "auto" # -> "auto" or "expanded" or "collapsed"
    )
    
    # Hide default streamlit menu and footer
    hide_default_st_style = "<style> #MainMenu {visibility: hidden;s} footer {visibility: hidden;} </style>"
    st.markdown(body=hide_default_st_style, unsafe_allow_html=True)

    # Initialize streamlit session variables
    if("init_var" not in st.session_state):
        st.session_state['init_var'] = False
    
    # Show sidebar content
    showSidebarContent()

    # Show page content
    showPageContent()

# Main function
def main() -> None:
    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Call Streamlit page function
    homePage()

# Main handler
if __name__ == '__main__':
    main()