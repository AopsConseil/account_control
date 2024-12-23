import streamlit as st
import functions as fn
import os



# streamlit run "C:\Users\Yacine AMMI\Yacine\Notebooks\AOPS\Scripts\Controle Fichiers\control_app.py"--server.maxUploadSize 3000


def init_session_state_data():
    st.session_state.renamed_preview = []
    st.session_state.formatted_preview = []
    st.session_state.df = None
    st.session_state.final_df = None
    st.session_state.df_1 = None
    st.session_state.warnings_bad = None
    st.session_state.tmp = None
    st.session_statecontrolled = False

def main():
    # Get the current directory (where your app is running)
    current_dir = os.path.dirname(__file__)

    # Use relative paths to the JSON, images, and other resources
    json_path = os.path.join(current_dir, 'resources', 'renaming.json')
    MAPPINGS_FILE = os.path.join(current_dir, 'resources', 'mappings.json')
    page_ico = os.path.join(current_dir, 'resources', 'tab_logo.png')
    logo = os.path.join(current_dir, 'resources', 'Logo_AOPS_conseil.png')
    title = 'Outil de :orange[Contrôle] des Fichiers '

    st.set_page_config(layout="wide", page_title='Controle des Fichiers', page_icon=page_ico)
    
    fn.init_appearance(logo, title)
    
    if 'type' not in st.session_state :
        st.session_state.type_fichier = None
        st.session_state.type = None
        st.session_state.type_risque = None
        st.session_state.assr = None
        init_session_state_data()
    
    cols = st.columns([1,2,2])
    

    # selectionner le type de fichier ["Santé", "Prevoyance"] 
    with cols[0]:
        
        st.session_state.type_fichier = st.radio('Type de fichier', ["santé", "prévoyance"], help='Sélectionner le type de fichier', horizontal=True, index=None)
        types_dispo, assr_dispo = fn.get_types_assureurs(type_fichier=st.session_state.type_fichier, json_path=json_path)
        
    if st.session_state.type_fichier == "santé":
        
        # selectionner le type de fichier ["prestations", "cotisations", "effectifs"] 
        st.session_state.type = cols[1].selectbox(label="Selectionnez le type de fichier", options=types_dispo, placeholder='Type de fichier', index=None, key="type_w")
        if st.session_state.type is not None:
            
            # selectionner l'assureur
            st.session_state.assr = cols[2].selectbox(label="Selectionnez l'assureur", options=assr_dispo, placeholder='Assureur', index=None, key="assr_w")

    elif st.session_state.type_fichier == "prévoyance":
        
        with cols[1]:
            st_cols = st.columns(2)
            
            # selectionner le type de fichier ["prestations", "cotisations"] 
            st.session_state.type = st_cols[0].radio(label="Selectionnez le type de fichier", options=types_dispo, index=None, horizontal=True)
            if st.session_state.type == 'prestations':
                
                # selectionner le type de risque ["prestations", "cotisations"]
                st.session_state.type_risque = st_cols[1].selectbox(label="Selectionnez le type de risque", options=['mensualisation',
                                                                                                                'incapacité',
                                                                                                                'invalidité',
                                                                                                                'décès'], 
                                                            placeholder='Type de risque', index=None, key="type_r")
            
            if (st.session_state.type is not None) and ((st.session_state.type_risque is not None) or (st.session_state.type == 'cotisations')):
                st.session_state.assr = cols[2].selectbox(label="Selectionnez l'assureur", options=assr_dispo, index=None, key="assr_w")            

    # uploaded_file = None

    if st.session_state.type_fichier and st.session_state.type and st.session_state.assr:
        
        rename_dict = fn.get_col_maps(type_fichier=st.session_state.type_fichier ,type_bdd=st.session_state.type,  assureur=st.session_state.assr, json_path=json_path)
        mandatory_cols = fn.mandatory_cols.get(st.session_state.type_fichier, {})[st.session_state.type]
        
        fn.upload_and_rename_multiple("Chargement des Fichiers", mandatory_cols=mandatory_cols, rename_dict=rename_dict, store_key='df', json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb', 'pkl', 'pickle'], convert_dtype=True, type_bdd=st.session_state.type, key="uploaded_files")
        
            #------------------------------------------------- AOPS Codification ------------------------------------------------------------------------------#
        if st.session_state.df is not None:
            if (st.session_state.type_fichier == 'santé') and(st.session_state.type == 'prestations'):
                if "code_acte" in st.session_state.df.columns:
                    fn.codification_aops(st.session_state.df)
                    
                            
            #------------------------------------------------- Format labels ------------------------------------------------------------------------------     
            
            if st.session_state.df is not None:
                
                st.divider()
                
                format_toggle = st.toggle('Mettre en forme')
                
                if format_toggle:
                    cols_to_map = ['niveau_couverture_fac', 'niveau_couverture_oblg', 'cat_assuré', 'type_bénéf']
                    cols_available = [col for col in cols_to_map if col in st.session_state.df.columns]
                    
                    if any(cols_available):
                        st.header("Mise en forme")
                        if 'niv_couv_edited_df' not in st.session_state:
                            # st.session_state.formatted_preview = st.session_state.renamed_preview.copy()
                            st.session_state.niv_couv_edited_df = None
                            st.session_state.niv_couv_oblg_edited_df = None
                            st.session_state.cat_assr_edited_df = None
                            st.session_state.type_bénéf_edited_df = None
                            st.session_state.mapped_cols = []

                        # if 'mappings' not in st.session_state:
                        st.session_state.mappings = fn.load_mappings(MAPPINGS_FILE)

                        cols = st.columns(2)
                        
                        for idx, col_to_map in enumerate(cols_available):
                            fn.handle_column_mapping(df=st.session_state.df, col_to_map=col_to_map, st_col=cols[idx % 2], session_state=st.session_state, MAPPINGS_FILE=MAPPINGS_FILE)
                        
                else:
                    st.session_state.final_df = st.session_state.df.copy()
                    
            #------------------------------------------------- Download option------------------------------------------------------------------------------
                if st.session_state.final_df is not None:
                    st.subheader('Résultat')
                    fn.preview_file(st.session_state.final_df)
                telechargement_expand = st.expander(fn.orange_markdown_string("Téléchargement"))
                with telechargement_expand:
                    fn.telechargement(st.session_state.final_df)
            #------------------------------------------------- General Control section------------------------------------------------------------------------------ 
            st.divider()
            if st.session_state.final_df is not None:
                control_général = st.toggle('Contrôle général', key="controle_general_togl")
                    
            if control_général:
                st.header('Contrôle général du fichier')
                with st.spinner('Chargement en cours ....'):
                    fn.resume_bdd(st.session_state.final_df, st.session_state.type)

            #------------------------------------------------- BAD Control section------------------------------------------------------------------------------
                st.divider()
                if  st.session_state.type_fichier == 'santé':
                    control_bad = st.toggle('Contrôle spécifique a la BAD santé')
                    
                if control_bad:
                    
                    st.header("Points de Contrôles BAD")
                    
            #------------------------------------------------- Upload T-1 ------------------------------------------------------------------------------                    
                    
                    mandatory_cols = ['id_bénéf', 'id_assuré', 'id_ent', 'siren']
                    # rename_dict = fn.get_col_maps(type_fichier=st.session_state.type_fichier ,type_bdd=st.session_state.type,  assureur=st.session_state.assr, json_path=json_path)
                    # st.session_state.df_1 = fn.upload_and_rename(title="Charger T-1", mandatory_cols=mandatory_cols, rename_dict=rename_dict, json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb', 'pkl', 'pickle'], key='df_1_up')
                    
                    fn.upload_and_rename_multiple(title="Charger T-1", mandatory_cols=mandatory_cols, rename_dict=rename_dict, store_key='df_1', json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb'], convert_dtype=True, type_bdd=st.session_state.type, key="df_1_up")

                    
                #------------------------------------------------- Control coherence and display warnings------------------------------------------------------------------------------
                    if st.session_state.type_fichier == 'santé':
                        if st.session_state.type in ['prestations', 'cotisations']:
                            st.session_state.tmp = None
                            # st.session_state.tmp = fn.upload_and_rename(title="Charger effectifs", mandatory_cols=mandatory_cols, rename_dict=rename_dict, json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb', 'pkl', 'pickle'], key='df_eff_up')
                            fn.upload_and_rename_multiple(title="Charger effectifs", mandatory_cols=mandatory_cols, rename_dict=rename_dict, store_key='tmp', json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb'], convert_dtype=True, type_bdd=st.session_state.type, key="df_eff_up")
                            if st.session_state.tmp is not None:
                                st.session_state.df_eff = st.session_state.tmp

                        elif  st.session_state.type == 'effectifs':
                            st.session_state.tmp = None
                            # st.session_state.tmp = fn.upload_and_rename(title="Charger prestations", mandatory_cols=mandatory_cols, rename_dict=rename_dict, json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb', 'pkl', 'pickle'], key='df_prest_up')
                            fn.upload_and_rename_multiple(title="Charger prestations", mandatory_cols=mandatory_cols, rename_dict=rename_dict, store_key='tmp', json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb'], convert_dtype=True, type_bdd=st.session_state.type, key="df_prest_up")
                            if st.session_state.tmp is not None:
                                st.session_state.df_prest = st.session_state.tmp
                                
                        # elif st.session_state.type == 'cotisations':
                        #     st.session_state.df_cot = fn.upload_and_rename(title="Charger prestations", mandatory_cols=mandatory_cols, rename_dict=rename_dict, json_path=json_path, types=['csv', 'xlsx', 'xls', 'xlsb', 'pkl', 'pickle'], key='df_prest_up')
                        

                #------------------------------------------------- Control BAD and display warnings------------------------------------------------------------------------------  
                    st_col1, st_col2 = st.columns([2, 1])
                
                    with st_col1:
                        dates = fn.get_interactive_quarters()
                        
                    st_col2.markdown("<div style='width: 1px; height: 28px'></div>", unsafe_allow_html=True)
                    if st_col2.button(f"Contrôler les {st.session_state.type.title()}"):
                        # Contrôle des données
                        
                        # Global control
                        st.session_state.warnings_bad =  fn.controle(st.session_state.final_df, type_bdd=st.session_state.type, assureur=st.session_state.assr, dft_1_raw=st.session_state.df_1, rename_dict=None, raise_err=False, dates=dates)
                        
                        # Controle if df_eff is uploaded
                        if 'df_eff' in st.session_state:
                            if st.session_state.df_eff is not None:
                                st.session_state.warnings_bad_ids = fn.id_verif(df_prest_cot_raw=st.session_state.final_df, df_effectifs_raw=st.session_state.df_eff, type_bdd=st.session_state.type, rename=False, inverse=False)
                                st.session_state.warnings_bad_ids_inverse = fn.id_verif(df_prest_cot_raw=st.session_state.final_df, df_effectifs_raw=st.session_state.df_eff, type_bdd=st.session_state.type, rename=False, inverse=True)
                        
                        # Contro if df_prest is uploaded
                        if 'df_prest' in st.session_state:
                            if st.session_state.df_prest is not None:
                                st.session_state.warnings_bad_ids = fn.id_verif(df_prest_cot_raw=st.session_state.df_prest, df_effectifs_raw=st.session_state.final_df, type_bdd=st.session_state.type, rename=False, inverse=False)
                                st.session_state.warnings_bad_ids_inverse = fn.id_verif(df_prest_cot_raw=st.session_state.df_prest, df_effectifs_raw=st.session_state.final_df, type_bdd=st.session_state.type, rename=False, inverse=True)
                        
                        # display results
                        if  st.session_state.warnings_bad is not None:
                            fn.display_warnings(st.session_state.warnings_bad, title="Contrôles BAD", header="Résultat")
                            
                        if  'warnings_bad_ids' in  st.session_state :
                            fn.display_warnings(st.session_state.warnings_bad_ids, title=f"{st.session_state.type.title()} vs Effectifs", header=f"IDs {st.session_state.type.title()} manquants dans Effectifs ")
                            
                        if  'warnings_bad_ids_inverse' in  st.session_state :
                            fn.display_warnings(st.session_state.warnings_bad_ids_inverse, title=f"Effectifs vs {st.session_state.type.title()}", header=f"IDs Effectifs manquants dans {st.session_state.type.title()}" )


if __name__ == "__main__":
    main()
