import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
from dataclasses import dataclass
from dataclasses import asdict
from dataclass_wizard import JSONWizard
import json
import keyboard

import pandas as pd

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master.geometry("1120x630")
        self.master.title('Hoi4 National Focus Maker')
        
        self.frame = tk.LabelFrame(self.master, width=300, height=120, padx=10, pady=10, bg="#E6E6E6", relief='solid', bd=1, text = "詳細")
        self.frame.grid_propagate(False)
        self.frame.grid(row=0,column=0)
        
        self.frame2 = tk.LabelFrame(self.master, width=300, height=480, padx=10, pady=10, bg="#E6E6E6", relief='solid', bd=1, text = "詳細")
        self.frame2.grid_propagate(False)
        self.frame2.grid(row=1,column=0)
        
        self.xbar = tk.Scrollbar(self.master, orient=HORIZONTAL)
        self.ybar = tk.Scrollbar(self.master, orient=VERTICAL)

        self.canvas = tk.Canvas(self.master, width=780, height=600, bg="#E6E6E6", relief='solid', bd=1, scrollregion=(0, 0, 780, 600), xscrollcommand=self.xbar.set, yscrollcommand=self.ybar.set)
        self.canvas.grid_propagate(False)
        self.canvas.grid(row=0,column=1,rowspan=2)
        self.canvas.bind('<Button-3>', self.select_canvas)
        self.canvas.bind('<Button-1>', self.select_canvas2)
        self.canvas.bind('<Button-2>', self.select_canvas3)
        self.canvas.bind('<Button2-Motion>', self.move_canvas)
        self.canvas.bind('<Shift-Button-3>', self.shift_select)
        self.xbar.grid(row=2,column=1,sticky=W+E)
        self.ybar.grid(row=0,column=2,rowspan=2,sticky=N+S)

        self.xbar['command'] = self.canvas.xview
        self.ybar['command'] = self.canvas.yview

        #メニュー作成
        self.menu_bar = tk.Menu(master) 
        self.master.config(menu=self.menu_bar) 
        
        #親メニュー
        self.menu_file = tk.Menu(master) 
        self.menu_bar.add_cascade(label='ファイル', menu=self.menu_file) 

        self.menu_file.add_command(label='開く', command=self.open_file) 
        self.menu_file.add_command(label='保存', command=self.save_file) 
        self.menu_file.add_command(label='名前をつけて保存', command=self.save_file) 
        self.menu_file.add_command(label='出力', command=self.export_file) 
        self.menu_file.add_command(label='出力(言語ファイル)', command=self.export_loc_file) 
        self.menu_file.add_separator() 
        self.menu_file.add_command(label='閉じる', command=self.close_display)
        
        self.popup = tk.Menu(self.master, tearoff=0)
        self.popup.add_command(label="作成", command=self.new_focus)
        self.popup.add_command(label="編集", command=self.edit_focus)
        self.popup.add_command(label="移動", command=self.move_focus)
        self.popup.add_separator()
        self.popup.add_command(label="接続", command=self.connect_focus)
        self.popup.add_command(label="排反", command=self.mutually_focus)
        self.popup.add_separator()
        self.popup.add_command(label="削除", command=self.remove_focus)

        self.popup2 = tk.Menu(self.master, tearoff=0)
        self.popup2.add_command(label="ここに接続", command=self.new_connect)
        self.popup2.add_command(label="接続を削除", command=self.delete_connect)
        self.popup2.add_command(label="キャンセル", command=self.cancel)

        self.popup3 = tk.Menu(self.master, tearoff=0)
        self.popup3.add_command(label="ここに移動", command=self.moved_focus)
        self.popup3.add_command(label="キャンセル", command=self.cancel)

        self.popup4 = tk.Menu(self.master, tearoff=0)
        self.popup4.add_command(label="ここと排反", command=self.new_mutually)
        self.popup4.add_command(label="排反状態を削除", command=self.delete_mutually)
        self.popup4.add_command(label="キャンセル", command=self.cancel)

        self.popup6 = tk.Menu(self.master, tearoff=0)
        self.popup6.add_command(label="接続(or)", command=self.and_connect)
        self.popup6.add_command(label="キャンセル", command=self.cancel)

        self.create_widgets()

    def create_widgets(self):
        ###EDIT FRAME### 
        self.label_country = tk.Label(self.frame, text='国家(TAG)')
        self.entry_country = tk.Entry(self.frame, width=20)
        self.label_focus_id = tk.Label(self.frame, text='NFid')
        self.entry_focus_id = tk.Entry(self.frame)
        self.button_submit = tk.Button(self.frame, width=8, command=self.submit)

        self.label_country.grid(row=0,column=0)
        self.entry_country.grid(row=0,column=1)
        self.label_focus_id.grid(row=1,column=0)
        self.entry_focus_id.grid(row=1,column=1,sticky=W+E)
        self.button_submit.grid(row=2,column=1)

        self.label_error = tk.Label(self.frame2)
        self.label_error.grid(row=100,column=0,columnspan=100)
        self.label_focus_x = tk.Label(self.frame2, text="x")
        self.entry_focus_x = tk.Entry(self.frame2, width=5)
        self.label_focus_y = tk.Label(self.frame2, text="y")
        self.entry_focus_y = tk.Entry(self.frame2, width=5)

        self.label_focus_name = tk.Label(self.frame2, text="Name")
        self.entry_focus_name = tk.Entry(self.frame2, width=30)

        self.label_focus_icon = tk.Label(self.frame2, text="Icon")
        option = ['Political', 'Research', 'Industry', 'Stability', 'War Support', 'Manpower', 'Political Violence', 'Occupation Costs', 'Territorial Expansion', 'Inflation', 'Congress', 'Autonomy', 'Church Authority', 'Caudillo Rebellion', 'Spanish Civil War', 'Carlist Uprising', 'Internal Affairs', 'Debt to the I.F.C.', 'Kurdistan', 'Kemalism', 'Traditionalism', 'Political Paranoia', 'Propaganda', 'Army Experience', 'Navy Experience', 'Air Experience', "Mussolini's Missions", 'Balance of Power', 'Military Readiness']
        option2 = ['GFX_focus_AST_never_gallipoli', 'GFX_focus_AST_rats_tobruk', 'GFX_focus_AST_squander_bug', 'GFX_focus_AST_war_japan', 'GFX_focus_attack_australia', 'GFX_focus_attack_britain', 'GFX_focus_attack_canada', 'GFX_focus_attack_china', 'GFX_focus_attack_france', 'GFX_focus_attack_germany', 'GFX_focus_attack_india', 'GFX_focus_attack_japan', 'GFX_focus_attack_mexico', 'GFX_focus_attack_soviet', 'GFX_focus_attack_switzerlan', 'GFX_focus_befriend_italy', 'GFX_focus_BUL_balkan_federation_of_socialist_republic', 'GFX_focus_BUL_bulgarian_administration_of_the_balkan', 'GFX_focus_BUL_bulgaria_on_the_three_sea', 'GFX_focus_BUL_condemn_macedonian_organization', 'GFX_focus_BUL_consolidate_the_third_bulgarian_state', 'GFX_focus_BUL_cooperate_with_the_zveno', 'GFX_focus_BUL_destroy_the_zveno', 'GFX_focus_BUL_form_a_regency_council', 'GFX_focus_BUL_found_the_brannik', 'GFX_focus_BUL_free_balkan_state', 'GFX_focus_BUL_guardians_of_the_balkan', 'GFX_focus_BUL_oppose_the_royal_dictatorship', 'GFX_focus_BUL_plot_against_bori', 'GFX_focus_BUL_power_to_the_tsar', 'GFX_focus_BUL_promote_bulgarian_nationalism', 'GFX_focus_BUL_prussia_of_the_balkan', 'GFX_focus_BUL_restore_the_bulgarian_patriarchate', 'GFX_focus_BUL_support_macedonian_organization', 'GFX_focus_BUL_supremacy_on_the_bosporu', 'GFX_focus_BUL_the_fate_of_the_balkan', 'GFX_focus_BUL_the_fatherland_front', 'GFX_focus_BUL_the_peoples_republic_of_bulgaria', 'GFX_focus_BUL_the_return_of_ferdinan', 'GFX_focus_BUL_the_third_bulgarian_empire', 'GFX_focus_BUL_the_unification_of_the_balkan', 'GFX_focus_chi_army_reform', 'GFX_focus_chi_british_cooperation', 'GFX_focus_chi_collaboration_with_the_japanese', 'GFX_focus_chi_cooperation_with_the_communist', 'GFX_focus_chi_cooperation_with_the_nationalist', 'GFX_focus_chi_examination_yuan', 'GFX_focus_chi_flying_tiger', 'GFX_focus_chi_legislative_yuan', 'GFX_focus_chi_mission_to_germany', 'GFX_focus_chi_mission_to_the_soviet_union', 'GFX_focus_chi_mission_to_the_u', 'GFX_focus_chi_one_china_policy', 'GFX_focus_chi_proclaim_rival_government', 'GFX_focus_chi_reach_out_to_france', 'GFX_focus_chi_united_front', 'GFX_focus_chi_whampoa_military_academy', 'GFX_focus_cze_german_puppet', 'GFX_focus_cze_military_aeronautical_institute', 'GFX_focus_cze_military_research_institute', 'GFX_focus_eng_bring_the_dominions_back_into_the_fol', 'GFX_focus_eng_chiefs_of_staff_committee', 'GFX_focus_eng_concessions_to_the_trade_union', 'GFX_focus_eng_crush_the_dream', 'GFX_focus_eng_decolonization', 'GFX_focus_eng_expose_the_belly_of_the_bear', 'GFX_focus_eng_global_defense', 'GFX_focus_eng_god_save_the_king', 'GFX_focus_eng_imperial_federation', 'GFX_focus_eng_liberate_the_home_of_marx', 'GFX_focus_eng_motion_of_no_confidence', 'GFX_focus_eng_move_to_secure_the_dominion', 'GFX_focus_eng_organise_the_blackshirt', 'GFX_focus_eng_special_air_service', 'GFX_focus_eng_the_kings_party', 'GFX_focus_eng_the_sun_never_set', 'GFX_focus_eng_unite_the_anglosphere', 'GFX_focus_EST_era_of_silence', 'GFX_focus_EST_estonia_is_scandinavia', 'GFX_focus_EST_fight_the_vap', 'GFX_focus_EST_national_pride_in_finlan', 'GFX_focus_EST_rally_the_nation', 'GFX_focus_EST_republican_defence_league', 'GFX_focus_ETH_addressing_the_league_of_nation', 'GFX_focus_ETH_adopt_the_lira', 'GFX_focus_ETH_african_union', 'GFX_focus_ETH_african_wildfire', 'GFX_focus_ETH_amedeos_feast_of_maskal', 'GFX_focus_ETH_an_arabic_base', 'GFX_focus_ETH_an_empire_in_the_shade_of_the_sun', 'GFX_focus_ETH_an_ethiopian_navy_in_exile', 'GFX_focus_ETH_boarding_the_train', 'GFX_focus_ETH_boots_on_the_shore', 'GFX_focus_ETH_callout_to_the_worl', 'GFX_focus_ETH_compensation', 'GFX_focus_ETH_consolidate_east_africa', 'GFX_focus_ETH_continuous_strengthen_the_black_lion', 'GFX_focus_ETH_continuous_supporting_the_arbegnoch', 'GFX_focus_ETH_develop_the_horn_of_africa', 'GFX_focus_ETH_ecole_militaire_haile_selassie_1er', 'GFX_focus_ETH_elect_of_go', 'GFX_focus_ETH_empower_the_ra', 'GFX_focus_ETH_expand_the_kebur_zabagna', 'GFX_focus_ETH_expand_the_levy', 'GFX_focus_ETH_freedom_at_gunpoint', 'GFX_focus_ETH_invest_in_the_east', 'GFX_focus_ETH_invest_in_the_north', 'GFX_focus_ETH_invest_in_the_west', 'GFX_focus_ETH_invite_italian_settler', 'GFX_focus_ETH_in_the_name_of_the_people', 'GFX_focus_ETH_jah', 'GFX_focus_ETH_keep_the_chitet', 'GFX_focus_ETH_lord_of_lor', 'GFX_focus_ETH_negusa-nagast', 'GFX_focus_ETH_northern_thrust', 'GFX_focus_ETH_organization_of_african_unity', 'GFX_focus_ETH_pan_africanism', 'GFX_focus_ETH_peacekeeping_force', 'GFX_focus_ETH_promote_the_war_heroe', 'GFX_focus_ETH_protector_of_the_somali', 'GFX_focus_ETH_rally_around_the_emperor', 'GFX_focus_ETH_re-convene_the_parliament', 'GFX_focus_ETH_reach_out_to_the_italian', 'GFX_focus_ETH_reform_the_currency', 'GFX_focus_ETH_replace_the_abuna', 'GFX_focus_ETH_restore_the_empire_of_axum', 'GFX_focus_ETH_scavenging_tactic', 'GFX_focus_ETH_soviet-ethiopian_trade_agreement', 'GFX_focus_ETH_support_from_the_japanese_communist', 'GFX_focus_ETH_sway_the_warlor', 'GFX_focus_ETH_the-italo_ethiopian_empire', 'GFX_focus_ETH_the_abuna', 'GFX_focus_ETH_the_african_union', 'GFX_focus_ETH_the_emperor_stay', 'GFX_focus_ETH_the_ethiopian_air_force', 'GFX_focus_ETH_the_heir_of_solomon', 'GFX_focus_ETH_the_heroes_of_ethiopa', 'GFX_focus_ETH_the_king_of_king', 'GFX_focus_ETH_the_lion_and_the_sun', 'GFX_focus_ETH_the_lion_stands_firm', 'GFX_focus_ETH_the_one_true_heir_of_solomon', 'GFX_focus_ETH_the_patriot', 'GFX_focus_ETH_the_rif', 'GFX_focus_ETH_the_second_italo_ethiopian_war', 'GFX_focus_ETH_the_state_bank_of_ethiopia', 'GFX_focus_ETH_unification_of_the_habesha', 'GFX_focus_ETH_unite_the_afar', 'GFX_focus_ETH_victory_in_the_desert', 'GFX_focus_focus_fra_border', 'GFX_focus_focus_fra_down_marianne', 'GFX_focus_focus_fra_fascist_threat', 'GFX_focus_focus_fra_intervention_spain', 'GFX_focus_focus_fra_liberte_egalite_solidarite', 'GFX_focus_focus_fra_maqui', 'GFX_focus_focus_fra_national_resistance_council', 'GFX_focus_focus_fra_orleans_restoration', 'GFX_focus_focus_fra_ratify_stresa', 'GFX_focus_focus_fra_revolution_upmost', 'GFX_focus_focus_fra_third_empire', 'GFX_focus_fra_devalue_the_franc', 'GFX_focus_fra_french_union', 'GFX_focus_fra_intervention_spain', 'GFX_focus_fra_le_deluge', 'GFX_focus_fra_loyalty_stalin', 'GFX_focus_fra_loyalty_trotzky', 'GFX_focus_fra_milice', 'GFX_focus_fra_ratify_stresa', 'GFX_focus_fra_regiment_normandie', 'GFX_focus_generic_adriatic_sea_focu', 'GFX_focus_generic_aegean_sea_focu', 'GFX_focus_generic_africa_defense', 'GFX_focus_generic_africa_factory', 'GFX_focus_generic_africa_infrastructure', 'GFX_focus_generic_africa_liberation', 'GFX_focus_generic_africa_naval', 'GFX_focus_generic_africa_production', 'GFX_focus_generic_aircraft_production', 'GFX_focus_generic_air_defense', 'GFX_focus_generic_aluminum', 'GFX_focus_generic_annex_country', 'GFX_focus_generic_annex_country_2', 'GFX_focus_generic_anti_fascist_diplomacy', 'GFX_focus_generic_armored_air_support', 'GFX_focus_generic_army_tanks2', 'GFX_focus_generic_attack_bulgaria', 'GFX_focus_generic_attack_communist_spain', 'GFX_focus_generic_attack_cypru', 'GFX_focus_generic_attack_denmark', 'GFX_focus_generic_attack_ethiopia', 'GFX_focus_generic_attack_finlan', 'GFX_focus_generic_attack_greece', 'GFX_focus_generic_attack_iran', 'GFX_focus_generic_attack_kurdistan', 'GFX_focus_generic_attack_mongolia', 'GFX_focus_generic_attack_nationalist_spain', 'GFX_focus_generic_attack_norway', 'GFX_focus_generic_attack_portugal', 'GFX_focus_generic_attack_republican_spain', 'GFX_focus_generic_attack_romania', 'GFX_focus_generic_attack_sweden', 'GFX_focus_generic_attack_turkey', 'GFX_focus_generic_attack_vichy_france', 'GFX_focus_generic_balkans_focu', 'GFX_focus_generic_balkan_diplomacy', 'GFX_focus_generic_baltic_entente', 'GFX_focus_generic_befriend_afghanistan', 'GFX_focus_generic_befriend_albania', 'GFX_focus_generic_befriend_bulgaria', 'GFX_focus_generic_befriend_communist_spain', 'GFX_focus_generic_befriend_cypru', 'GFX_focus_generic_befriend_greece', 'GFX_focus_generic_befriend_kurdistan', 'GFX_focus_generic_befriend_nationalist_spain', 'GFX_focus_generic_befriend_portugal', 'GFX_focus_generic_befriend_republican_spain', 'GFX_focus_generic_befriend_saudi_arabia', 'GFX_focus_generic_befriend_sinkiang', 'GFX_focus_generic_befriend_turkey', 'GFX_focus_generic_black_sea_focu', 'GFX_focus_generic_camel_corp', 'GFX_focus_generic_catholic_dominion', 'GFX_focus_generic_china1', 'GFX_focus_generic_coastal_fort', 'GFX_focus_generic_coffee', 'GFX_focus_generic_combined_arm', 'GFX_focus_generic_commonwealth_build_infantry', 'GFX_focus_generic_concession', 'GFX_focus_generic_conspiracy', 'GFX_focus_generic_copy_plane_design', 'GFX_focus_generic_court', 'GFX_focus_generic_cruiser2', 'GFX_focus_generic_cryptologic_bomb', 'GFX_focus_generic_destroyer', 'GFX_focus_generic_develop_eritrea', 'GFX_focus_generic_develop_ethiopia', 'GFX_focus_generic_develop_libya', 'GFX_focus_generic_develop_somalilan', 'GFX_focus_generic_diplomatic_treaty', 'GFX_focus_generic_energy', 'GFX_focus_generic_fascist_propaganda', 'GFX_focus_generic_fascist_troop', 'GFX_focus_generic_forest_brother', 'GFX_focus_generic_free_iberia', 'GFX_focus_generic_home_defense', 'GFX_focus_generic_horse_stu', 'GFX_focus_generic_hydroelectric_energy', 'GFX_focus_generic_improve_roa', 'GFX_focus_generic_improve_the_administration', 'GFX_focus_generic_industry_1', 'GFX_focus_generic_industry_2', 'GFX_focus_generic_industry_3', 'GFX_focus_generic_infiltration', 'GFX_focus_generic_italy_first', 'GFX_focus_generic_italy_propaganda', 'GFX_focus_generic_japanese_imperial_glory', 'GFX_focus_generic_join_comintern', 'GFX_focus_generic_land_reclamation', 'GFX_focus_generic_league_of_nation', 'GFX_focus_generic_license_production', 'GFX_focus_generic_little_entente', 'GFX_focus_generic_long_range_aircraft', 'GFX_focus_generic_manpower', 'GFX_focus_generic_mediterranean_sea_focu', 'GFX_focus_generic_midget_submarine', 'GFX_focus_generic_military_academy', 'GFX_focus_generic_military_dictatorship', 'GFX_focus_generic_military_mission', 'GFX_focus_generic_mine_warfare', 'GFX_focus_generic_monarchy_1', 'GFX_focus_generic_monarchy_2', 'GFX_focus_generic_multi_role_aircraft', 'GFX_focus_generic_national_security', 'GFX_focus_generic_navy_battleship2', 'GFX_focus_generic_paratrooper', 'GFX_focus_generic_polish_deal', 'GFX_focus_generic_pope', 'GFX_focus_generic_population_growth', 'GFX_focus_generic_provoke_border_clashe', 'GFX_focus_generic_railroa', 'GFX_focus_generic_railway_gun', 'GFX_focus_generic_refit_civilian_ship', 'GFX_focus_generic_royal_wedding', 'GFX_focus_generic_rubber', 'GFX_focus_generic_scandinavian_alliance', 'GFX_focus_generic_scandinavia_flag', 'GFX_focus_generic_secret_service_agency', 'GFX_focus_generic_self_management', 'GFX_focus_generic_self_propelled_gun', 'GFX_focus_generic_socialist_science', 'GFX_focus_generic_soviet_politic', 'GFX_focus_generic_spread_fascism', 'GFX_focus_generic_steel', 'GFX_focus_generic_stockpile_fuel', 'GFX_focus_generic_strike_at_democracy1', 'GFX_focus_generic_strike_at_democracy2', 'GFX_focus_generic_strike_at_democracy3', 'GFX_focus_generic_support_the_left_right', 'GFX_focus_generic_tankette', 'GFX_focus_generic_tank_air_support', 'GFX_focus_generic_tank_production', 'GFX_focus_generic_the_giant_wake', 'GFX_focus_generic_the_suez', 'GFX_focus_generic_torpedo_production', 'GFX_focus_generic_treaty', 'GFX_focus_generic_truck', 'GFX_focus_generic_tungsten', 'GFX_focus_generic_vatican_agent', 'GFX_focus_generic_vatican_state', 'GFX_focus_generic_vichy_france_triumphant', 'GFX_focus_generic_women_in_military', 'GFX_focus_ger_accept_british_naval_dominance', 'GFX_focus_ger_assassinate_mussolini', 'GFX_focus_ger_break_anglo_french_colonial_hegemony', 'GFX_focus_ger_bulwark_against_bolshevism', 'GFX_focus_ger_great_red_menace', 'GFX_focus_ger_oppose_hitler', 'GFX_focus_ger_reichskommisariat', 'GFX_focus_ger_return_of_the_kaiser', 'GFX_focus_ger_revive_kaiserreich', 'GFX_focus_ger_strike_at_the_source', 'GFX_focus_GRE_an_orthodox_state', 'GFX_focus_GRE_a_land_of_mountain', 'GFX_focus_GRE_a_long_and_proud_tradition', 'GFX_focus_GRE_bedrock_of_balkan_stability', 'GFX_focus_GRE_byzantine_themata', 'GFX_focus_GRE_following_in_the_footsteps_of_giant', 'GFX_focus_GRE_hellenic_armed_force', 'GFX_focus_GRE_metaxism', 'GFX_focus_GRE_reevaluating_the_drachma', 'GFX_focus_GRE_resurrecting_the_megali_idea', 'GFX_focus_GRE_reviving_the_double_headed_eagle', 'GFX_focus_GRE_reviving_the_spartan_warrior_spirit', 'GFX_focus_GRE_stage_an_incident_in_the_bosporu', 'GFX_focus_hol_abandon_the_gold_standar', 'GFX_focus_hol_continue_the_war_in_batavia', 'GFX_focus_hol_daf', 'GFX_focus_hol_fokker', 'GFX_focus_hol_gateway_to_europe', 'GFX_focus_hol_legacy_of_the_de_zeven_provincien_mutiny', 'GFX_focus_hol_liberation', 'GFX_focus_hol_oranje_boven', 'GFX_focus_hol_philip', 'GFX_focus_hol_prepare_the_inundation_line', 'GFX_focus_hol_the_foundations_of_defense', 'GFX_focus_hol_the_fourth_ally', 'GFX_focus_hol_the_only_man_in_the_dutch_government', 'GFX_focus_hol_the_zuiderzee_work', 'GFX_focus_hol_united_netherlan', 'GFX_focus_hol_war_on_pacifism', 'GFX_focus_hun_assassinate_horthy', 'GFX_focus_hun_elect_a_king', 'GFX_focus_intervention_spain_nationalist', 'GFX_focus_intervention_spain_republic', 'GFX_focus_invite_finlan', 'GFX_focus_invite_romania', 'GFX_focus_invite_yugoslavia', 'GFX_focus_ITA_albanian_fascist_militia', 'GFX_focus_ITA_albanian_irredentism', 'GFX_focus_ITA_alcide_de_gasperi', 'GFX_focus_ITA_alpine_division', 'GFX_focus_ITA_a_colonial_empire', 'GFX_focus_ITA_banda_carita', 'GFX_focus_ITA_battaglioni_m', 'GFX_focus_ITA_bend_the_bar', 'GFX_focus_ITA_bersaglieri', 'GFX_focus_ITA_blackshirt', 'GFX_focus_ITA_by_blood_alone', 'GFX_focus_ITA_capo_supremo', 'GFX_focus_ITA_cavalry_charge', 'GFX_focus_ITA_comandante_diavolo', 'GFX_focus_ITA_communist_leadership', 'GFX_focus_ITA_corpo_volontari_della_liberta', 'GFX_focus_ITA_culto_del_duce', 'GFX_focus_ITA_decima_flottiglia_ma', 'GFX_focus_ITA_democratic_leadership', 'GFX_focus_ITA_depose_mussolini', 'GFX_focus_ITA_devaluate_the_lire', 'GFX_focus_ITA_dino_grandi', 'GFX_focus_ITA_ferrea_mole_ferreo_cuore', 'GFX_focus_ITA_fiat_ansaldo_duopoly', 'GFX_focus_ITA_garibaldi_legion', 'GFX_focus_ITA_generic_fascist_worker', 'GFX_focus_ITA_grande_rivolta_rurale', 'GFX_focus_ITA_greater_italy', 'GFX_focus_ITA_guardia_nazionale_repubblicana', 'GFX_focus_ITA_il_sol_dell_avvenire', 'GFX_focus_ITA_imperial_recognition', 'GFX_focus_ITA_italian_hegemony', 'GFX_focus_ITA_italian_irredentism', 'GFX_focus_ITA_italo_balbo', 'GFX_focus_ITA_king_vittorio', 'GFX_focus_ITA_liberate_gramsci', 'GFX_focus_ITA_liberation_or_death', 'GFX_focus_ITA_mare_nostrum', 'GFX_focus_ITA_milizia_marittima_di_artiglieria', 'GFX_focus_ITA_ministry_of_italian_africa', 'GFX_focus_ITA_modernize_ansaldo_facilitie', 'GFX_focus_ITA_moschettieri_del_duce', 'GFX_focus_ITA_new_horizon', 'GFX_focus_ITA_northern_industry', 'GFX_focus_ITA_peasants_rise', 'GFX_focus_ITA_redirect_alfa_romeo_production', 'GFX_focus_ITA_southern_industry', 'GFX_focus_ITA_strengthen_ascari_corp', 'GFX_focus_ITA_subdue_the_sentinel', 'GFX_focus_ITA_the_italian_republic', 'GFX_focus_ITA_the_new_emperor_of_ethiopia', 'GFX_focus_ITA_the_social_republic_prevail', 'GFX_focus_ITA_topple_amhara_ruler', 'GFX_focus_ITA_to_live_as_a_lion', 'GFX_focus_ITA_workers_union', 'GFX_focus_jap_cast_the_die', 'GFX_focus_jap_manchurian_project', 'GFX_focus_jap_pacific_guardian', 'GFX_focus_jap_showa_restoration', 'GFX_focus_jap_spiritual_mobilization', 'GFX_focus_jap_strike_south', 'GFX_focus_jap_zaibatsu', 'GFX_focus_jap_zero', 'GFX_focus_LAT_aizsargi', 'GFX_focus_LAT_banish_clemin', 'GFX_focus_LAT_latvia_for_latvian', 'GFX_focus_LAT_lightning_strike', 'GFX_focus_LAT_merge_presidential_title', 'GFX_focus_LAT_ostlan', 'GFX_focus_LAT_renew_kviesis_term', 'GFX_focus_LAT_suspend_constitution_of_latvia', 'GFX_focus_LAT_the_old_way', 'GFX_focus_LAT_threat_on_our_border', 'GFX_focus_LIT_claim_livonia', 'GFX_focus_LIT_exile_voldemara', 'GFX_focus_LIT_free_voldemara', 'GFX_focus_LIT_king_of_polan', 'GFX_focus_LIT_new_kind_of_iron_wolf', 'GFX_focus_LIT_organize_the_iron_wolf', 'GFX_focus_LIT_reclaim_courlan', 'GFX_focus_LIT_restore_order', 'GFX_focus_LIT_restore_the_grand_duchy', 'GFX_focus_LIT_support_polish_fascist', 'GFX_focus_man_claim_the_mandate_of_heaven', 'GFX_focus_mex_arrest_general_cedillo', 'GFX_focus_mex_caudillo_private_armie', 'GFX_focus_mex_exile_calle', 'GFX_focus_mex_jefe_maximo', 'GFX_focus_mex_privatisation', 'GFX_focus_mex_redeem_aztlan', 'GFX_focus_mex_restore_the_army_of_christ', 'GFX_focus_mex_soldadera', 'GFX_focus_mex_support_general_cedillo', 'GFX_focus_mex_triumph_over_the_cristero', 'GFX_focus_NZL_bob_semple_tank', 'GFX_focus_POL_ban_nazi_party', 'GFX_focus_POL_beck_ribbentrop', 'GFX_focus_POL_belarus_army', 'GFX_focus_POL_clamp_down_on_danzig', 'GFX_focus_POL_colonial_league', 'GFX_focus_POL_common_organization_of_society', 'GFX_focus_POL_complete_april_constitution', 'GFX_focus_POL_consolidate_sanation_government', 'GFX_focus_POL_cossack_king', 'GFX_focus_POL_develop_polish_shipbuilding', 'GFX_focus_POL_end_the_regency', 'GFX_focus_POL_expand_polish_intelligence', 'GFX_focus_POL_habsburg', 'GFX_focus_POL_nationalist_education', 'GFX_focus_POL_OZON', 'GFX_focus_POL_plan_east', 'GFX_focus_POL_plan_west', 'GFX_focus_POL_polish_revanchism', 'GFX_focus_POL_prepare_for_the_inevitable', 'GFX_focus_POL_prussia_line', 'GFX_focus_POL_reach_out_to_underground_state', 'GFX_focus_POL_reassert_silesian_claim', 'GFX_focus_POL_resistance', 'GFX_focus_POL_riot_of_37', 'GFX_focus_POL_romania_bridgehead_strategy', 'GFX_focus_POL_sanation_left', 'GFX_focus_POL_sanation_right', 'GFX_focus_POL_support_global_falangism', 'GFX_focus_POL_the_castle', 'GFX_focus_POL_the_four_year_plan', 'GFX_focus_POL_ukrainian_army', 'GFX_focus_POL_warsaw_main_station', 'GFX_focus_por_concordat', 'GFX_focus_por_estado_novo', 'GFX_focus_por_iberian_summit', 'GFX_focus_por_latin_american_communism', 'GFX_focus_por_limited_self_rule', 'GFX_focus_por_luso_tropicalism', 'GFX_focus_por_portuguese_legion', 'GFX_focus_por_reclaim_crown_jewel', 'GFX_focus_por_recover_brazil', 'GFX_focus_por_recover_latin_america', 'GFX_focus_por_remember_olivenca', 'GFX_focus_por_salazar', 'GFX_focus_por_the_fifth_empire', 'GFX_focus_por_the_kingdom_reunite', 'GFX_focus_por_the_pink_map', 'GFX_focus_por_workers_of_iberia', 'GFX_focus_prc_agrarian_socialism', 'GFX_focus_prc_infiltration', 'GFX_focus_prc_maoism', 'GFX_focus_prc_proclaim_the_peoples_republic', 'GFX_focus_prc_remove_chiang_kai_shek', 'GFX_focus_prc_social_democracy', 'GFX_focus_proclaim_the_restauration_of_austria_hungary', 'GFX_focus_RAJ_all_india_forward_bloc', 'GFX_focus_RAJ_british_investor', 'GFX_focus_RAJ_clamp_down_on_corruption', 'GFX_focus_RAJ_indianisation_of_army', 'GFX_focus_RAJ_indian_gentlemen_offcer', 'GFX_focus_RAJ_indian_gurkha', 'GFX_focus_RAJ_lions_of_the_great_war', 'GFX_focus_RAJ_seek_help_from_germany', 'GFX_focus_RAJ_seek_help_from_soviet', 'GFX_focus_RAJ_two_nation_theory', 'GFX_focus_renounce_the_treaty_of_triannon', 'GFX_focus_research', 'GFX_focus_research2', 'GFX_focus_rocketry', 'GFX_focus_rom_abdicate', 'GFX_focus_rom_coup', 'GFX_focus_rom_handle_king', 'GFX_focus_rom_parties_en', 'GFX_focus_rom_preserve_romania', 'GFX_focus_rom_royal_dictatorship', 'GFX_focus_SAF_colonialist_crusade', 'GFX_focus_SAF_german_coup', 'GFX_focus_SAF_secure_africa', 'GFX_focus_SAF_support_ossewabrandwag', 'GFX_focus_secret_rearmament', 'GFX_focus_SOV_ally_bukharinist', 'GFX_focus_SOV_ally_zinovyevist', 'GFX_focus_SOV_approach_primakov', 'GFX_focus_SOV_approach_semyonov', 'GFX_focus_SOV_approach_tukahchevsky', 'GFX_focus_SOV_baltic_security', 'GFX_focus_SOV_behead_the_snake', 'GFX_focus_SOV_breadbasket_of_the_union', 'GFX_focus_SOV_builder_of_the_red_army', 'GFX_focus_SOV_bukharan_republic', 'GFX_focus_SOV_bukharinist', 'GFX_focus_SOV_father_of_nation', 'GFX_focus_SOV_flying_club', 'GFX_focus_SOV_free_Rutenia', 'GFX_focus_SOV_international_union_of_soviet_republic', 'GFX_focus_SOV_ivan_plays_baseball', 'GFX_focus_SOV_merge_plant', 'GFX_focus_SOV_military_purge', 'GFX_focus_SOV_mobilization_plan', 'GFX_focus_SOV_my_brothers_keeper', 'GFX_focus_SOV_old_eastern_empire', 'GFX_focus_SOV_organization_centralization_discipline', 'GFX_focus_SOV_organize_wrecker', 'GFX_focus_SOV_pacific_empire', 'GFX_focus_SOV_panslavic_nationalism', 'GFX_focus_SOV_patriarch_of_all_russia', 'GFX_focus_SOV_penal_battalion', 'GFX_focus_SOV_proclaim_soviet_hegemony', 'GFX_focus_SOV_purge_bukharinist', 'GFX_focus_SOV_purge_trotskyist', 'GFX_focus_SOV_purge_zinovyevist', 'GFX_focus_SOV_rebuild_the_savior_cathedral', 'GFX_focus_SOV_recover_alaska', 'GFX_focus_SOV_reinforce_eastern_naval_base', 'GFX_focus_SOV_reinforce_northern_naval_base', 'GFX_focus_SOV_reinforce_southern_naval_base', 'GFX_focus_SOV_reinforce_western_naval_base', 'GFX_focus_SOV_restore_cossack_unit', 'GFX_focus_SOV_socialism_in_one_country', 'GFX_focus_SOV_south_manchuria_railway', 'GFX_focus_SOV_stalins_cult_of_personality', 'GFX_focus_SOV_support_spanish_poum', 'GFX_focus_SOV_the_comecon', 'GFX_focus_SOV_the_defense_of_moscow', 'GFX_focus_SOV_the_glory_of_the_red_army_alternative', 'GFX_focus_SOV_the_glory_of_the_red_army_communism', 'GFX_focus_SOV_the_last_purge', 'GFX_focus_SOV_the_path_of_marxism_leninism', 'GFX_focus_SOV_the_road_of_life', 'GFX_focus_SOV_the_supreme_soviet', 'GFX_focus_SOV_the_true_tsar', 'GFX_focus_SOV_third_rome', 'GFX_focus_SOV_transcaucasian_republic', 'GFX_focus_SOV_womens_fascist_movement', 'GFX_focus_SOV_women_in_aviation', 'GFX_focus_SOV_zemsky_sobor', 'GFX_focus_SOV_zinovyevist', 'GFX_focus_spa_caudillo_of_spain', 'GFX_focus_spa_eliminate_the_carlist', 'GFX_focus_spa_fuse_the_partie', 'GFX_focus_spa_no_compromise_on_carlist_ideal', 'GFX_focus_spa_save_the_alcazar', 'GFX_focus_spa_strengthen_the_supreme_reality_of_spain', 'GFX_focus_spa_supremacy_of_the_communion', 'GFX_focus_spa_the_phalanx_ascendant', 'GFX_focus_spa_the_spanish_miracle', 'GFX_focus_spa_the_war_of_vengeance', 'GFX_focus_spa_unify_the_nationalist_front', 'GFX_focus_spr_anarchism_knows_no_border', 'GFX_focus_spr_class_war', 'GFX_focus_spr_crush_the_revolution', 'GFX_focus_spr_maintain_the_republic', 'GFX_focus_spr_masters_of_our_own_fate', 'GFX_focus_spr_no_pasaran', 'GFX_focus_spr_regional_defense_council_of_aragon', 'GFX_focus_spr_the_anti_fascist_workers_revolution', 'GFX_focus_spr_torchbearers_of_tomorrow', 'GFX_focus_spr_unify_the_london_bureau', 'GFX_focus_spr_war_of_independence', 'GFX_focus_SWI_abandon_neutrality', 'GFX_focus_SWI_aktion_nationaler_widerstan', 'GFX_focus_SWI_closer_ties_with_germany', 'GFX_focus_SWI_complete_siegfried_line', 'GFX_focus_SWI_connect_to_the_maginot_line', 'GFX_focus_SWI_continuous_build_up_military_readine', 'GFX_focus_SWI_continuous_support_active_militia', 'GFX_focus_SWI_dissolve_the_federal_council', 'GFX_focus_SWI_embrace_panoramaheim', 'GFX_focus_SWI_embrace_rote_drei', 'GFX_focus_SWI_establish_pro_helvetia', 'GFX_focus_SWI_expand_the_federation', 'GFX_focus_SWI_federal_police', 'GFX_focus_SWI_fortify_border_with_france', 'GFX_focus_SWI_fortify_border_with_germany', 'GFX_focus_SWI_fortify_border_with_italy', 'GFX_focus_SWI_gotthard_league', 'GFX_focus_SWI_guisans_coup', 'GFX_focus_SWI_helvetic_junta', 'GFX_focus_SWI_issue_war_bon', 'GFX_focus_SWI_neutrality_on_the_move', 'GFX_focus_SWI_new_eidgenossenschaft', 'GFX_focus_SWI_patriotic_shooting_club', 'GFX_focus_SWI_promote_guisan', 'GFX_focus_SWI_promote_henne', 'GFX_focus_SWI_recall_robert_tobler', 'GFX_focus_SWI_spirit_of_resistance', 'GFX_focus_SWI_spirit_of_saint_bernar', 'GFX_focus_SWI_swiss_guiding_principle', 'GFX_focus_SWI_the_national_redoubt', 'GFX_focus_TUR_crowning_ourselves_with_the_fin_ugor', 'GFX_focus_TUR_loosen_the_laws_on_secularism', 'GFX_focus_TUR_misak_i_milli', 'GFX_focus_TUR_pivot_to_the_past', 'GFX_focus_TUR_purge_the_kemalist', 'GFX_focus_TUR_ratify_the_six_arrow', 'GFX_focus_TUR_reconfigure_turkish_foreign_policy', 'GFX_focus_TUR_reform_the_balkan_pact', 'GFX_focus_TUR_support_the_golden_square', 'GFX_focus_TUR_taking_over_defense_of_the_gulf', 'GFX_focus_TUR_the_montreux_convention', 'GFX_focus_TUR_the_sun_language_theory', 'GFX_focus_TUR_treaty_of_saadaba', 'GFX_focus_TUR_turanist_ambition', 'GFX_focus_up_joan_of_arc', 'GFX_focus_usa_attack_italy', 'GFX_focus_usa_build_the_pentagon', 'GFX_focus_usa_escort_fighter', 'GFX_focus_usa_focus_on_asia', 'GFX_focus_usa_focus_on_europe', 'GFX_focus_usa_guarantee_the_american_dream', 'GFX_focus_usa_honor_the_confederacy', 'GFX_focus_usa_recruit_the_free_corp', 'GFX_focus_usa_reestablish_the_gold_standar', 'GFX_focus_usa_tank_destroyer_doctrine', 'GFX_focus_usa_union_representation_act', 'GFX_focus_usa_voter_registration_act', 'GFX_focus_wonderweapon', 'GFX_focus_YUG_autonomous_transylvania', 'GFX_focus_yug_banovina_of_croatia', 'GFX_focus_YUG_devolved_croatia', 'GFX_focus_YUG_dissolve_serbia', 'GFX_focus_YUG_divide_bosnia', 'GFX_focus_yug_ikaru', 'GFX_focus_yug_pan_slavic_congre', 'GFX_focus_yug_rogozarski', 'GFX_focus_YUG_safeguard_bosnia', 'GFX_focus_yug_zmaj', 'GFX_goal_anschlu', 'GFX_goal_anti_comintern_pact', 'GFX_goal_continuous_air_production', 'GFX_goal_continuous_armor_production', 'GFX_goal_continuous_boost_freedom', 'GFX_goal_continuous_def_against_influence', 'GFX_goal_continuous_increase_nu', 'GFX_goal_continuous_naval_production', 'GFX_goal_continuous_non_factory_construct', 'GFX_goal_continuous_reduce_training_time', 'GFX_goal_continuous_repairment', 'GFX_goal_continuous_research', 'GFX_goal_continuous_restrict_freedom', 'GFX_goal_continuous_suppression', 'GFX_goal_demand_sudetenlan', 'GFX_goal_generic_air_bomber', 'GFX_goal_generic_air_doctrine', 'GFX_goal_generic_air_fighter', 'GFX_goal_generic_air_fighter2', 'GFX_goal_generic_air_naval_bomber', 'GFX_goal_generic_air_production', 'GFX_goal_generic_alliance', 'GFX_goal_generic_allies_build_infantry', 'GFX_goal_generic_amphibious_assault', 'GFX_goal_generic_army_artillery', 'GFX_goal_generic_army_artillery2', 'GFX_goal_generic_army_doctrine', 'GFX_goal_generic_army_motorize', 'GFX_goal_generic_army_tank', 'GFX_goal_generic_attack_allie', 'GFX_goal_generic_axis_build_infantry', 'GFX_goal_generic_build_airforce', 'GFX_goal_generic_build_nay', 'GFX_goal_generic_build_tank', 'GFX_goal_generic_CAS', 'GFX_goal_generic_cavalry', 'GFX_goal_generic_construction', 'GFX_goal_generic_construction2', 'GFX_goal_generic_construct_civilian', 'GFX_goal_generic_construct_civ_factory', 'GFX_goal_generic_construct_infrastructure', 'GFX_goal_generic_construct_military', 'GFX_goal_generic_construct_mil_factory', 'GFX_goal_generic_construct_naval_dockyar', 'GFX_goal_generic_consumer_goo', 'GFX_goal_generic_dangerous_deal', 'GFX_goal_generic_defence', 'GFX_goal_generic_demand_territory', 'GFX_goal_generic_forceful_treaty', 'GFX_goal_generic_fortify_city', 'GFX_goal_generic_improve_relation', 'GFX_goal_generic_intelligence_exchange', 'GFX_goal_generic_major_alliance', 'GFX_goal_generic_major_war', 'GFX_goal_generic_military_deal', 'GFX_goal_generic_military_sphere', 'GFX_goal_generic_more_territorial_claim', 'GFX_goal_generic_national_unity', 'GFX_goal_generic_navy_anti_submarine', 'GFX_goal_generic_navy_battleship', 'GFX_goal_generic_navy_carrier', 'GFX_goal_generic_navy_cruiser', 'GFX_goal_generic_navy_doctrines_tactic', 'GFX_goal_generic_navy_submarine', 'GFX_goal_generic_neutrality_focu', 'GFX_goal_generic_occypy_start_war', 'GFX_goal_generic_occypy_states_coastal', 'GFX_goal_generic_occypy_states_ongoing_war', 'GFX_goal_generic_oil_refinery', 'GFX_goal_generic_political_pressure', 'GFX_goal_generic_position_armie', 'GFX_goal_generic_positive_trade_relation', 'GFX_goal_generic_production', 'GFX_goal_generic_production2', 'GFX_goal_generic_propaganda', 'GFX_goal_generic_radar', 'GFX_goal_generic_scientific_exchange', 'GFX_goal_generic_secret_weapon', 'GFX_goal_generic_small_arm', 'GFX_goal_generic_soviet_construction', 'GFX_goal_generic_special_force', 'GFX_goal_generic_support_communism', 'GFX_goal_generic_support_democracy', 'GFX_goal_generic_support_fascism', 'GFX_goal_generic_territory_or_war', 'GFX_goal_generic_trade', 'GFX_goal_generic_war_with_comintern', 'GFX_goal_generic_wolf_pack', 'GFX_goal_molotov_ribbentrop_pact', 'GFX_goal_poland_goal', 'GFX_goal_rhinelan', 'GFX_goal_support_fourth_int', 'GFX_goal_tfv_burn_the_royal_portrait', 'GFX_goal_tfv_can_compromise_with_quebec', 'GFX_goal_tfv_can_forced_quebec_conscription', 'GFX_goal_tfv_generic_tech_sharing', 'GFX_goal_tfv_sever_ties_with_uk', 'GFX_goal_tfv_smiling_buddha', 'GFX_goal_tfv_strengthen_commonwealth_tie', 'GFX_goal_tripartite_pact', 'GFX_goal_unknown', 'GFX_shine_mask', 'GFX_shine_overlay', 'GFX_untitl_focus_spa_unify_the_nationalist_front']
        variable = tk.StringVar ( )
        self.entry_focus_icon = ttk.Combobox (self.frame2 ,values = option2 ,textvariable = variable)

        self.label_focus_cost= tk.Label(self.frame2, text="コスト(x7)")
        self.entry_focus_cost = tk.Entry(self.frame2)

        variable2 = tk.StringVar ( )
        self.label_focus_category = tk.Label(self.frame2, text="分類")
        self.entry_focus_category = ttk.Combobox (self.frame2 ,values = option ,textvariable = variable2 )

        self.button_focus_edit = tk.Button(self.frame2, width = 5,text="反映", command=self.submit_focus)

        self.label_complete_reword = tk.Label(self.frame2,text='報酬')
        self.entry_complete_reword = scrolledtext.ScrolledText(self.frame2,width=8,height=6)

        #self.label_focus_prerequisite = tk.Label(self.frame2, text="前提")
        #self.entry_focus_prerequisite = tk.Listbox(self.frame2, height=1)
        #self.button_focus_prerequisite = tk.Button(self.frame2, text="追加")

        #self.label_focus_mutually = tk.Label(self.frame2, text="排反")
        #self.entry_focus_mutually = tk.Listbox(self.frame2, height=1)
        #self.button_focus_mutually = tk.Button(self.frame2, text="追加")

        self.label_focus_x.grid(row=0,column=2,sticky=E)
        self.entry_focus_x.grid(row=0,column=3,sticky=W)
        self.label_focus_y.grid(row=0,column=4,sticky=E)
        self.entry_focus_y.grid(row=0,column=5,sticky=W)
        self.label_focus_name.grid(row=1,column=1)
        self.entry_focus_name.grid(row=1,column=2,columnspan=4)
        self.label_focus_icon.grid(row=2,column=1)
        self.entry_focus_icon.grid(row=2,column=2,columnspan=4,sticky=E+W)
        self.label_focus_cost.grid(row=5,column=1)
        self.entry_focus_cost.grid(row=5,column=2,columnspan=4,sticky=E+W)
        self.label_focus_category.grid(row=6,column=1)
        self.entry_focus_category.grid(row=6,column=2,columnspan=4,sticky=E+W)
        self.label_complete_reword.grid(row=7,column=1,sticky=N)
        self.entry_complete_reword.grid(row=7,column=2,columnspan=4,sticky=E+W)
        self.button_focus_edit.grid(row=8,column=2,columnspan=4)
        #self.label_focus_prerequisite.grid(row=3,column=1,sticky=N)
        #self.entry_focus_prerequisite.grid(row=3,column=2,columnspan=4,sticky=E+W)
        #self.button_focus_prerequisite.grid(row=3,column=6)
        #self.label_focus_mutually.grid(row=4,column=1,sticky=N)
        #self.entry_focus_mutually.grid(row=4,column=2,columnspan=4,sticky=E+W)
        #self.button_focus_mutually.grid(row=4,column=6)

        ###INIT###
        self.sticks = []
        self.select_rect = self.canvas.create_rectangle(10, 10, 90, 90)
        self.error_text = self.canvas.create_text(0,0,text="")

        self.connecting = False
        self.moving = False
        self.mutualling = False
        self.if_selected = False
        self.multi = False
        self.multi_con = False
        self.multi_mov = False

        self.multi_select = multi_select([focus([], -1, None, -1, -1, None, -1, None, None)])
        self.boxs = [self.canvas.create_rectangle(0,0,0,0)]
        self.focus_list = focus_list('GER', 'focus', 780, 600, 0, [],[],[],[])
        self.entry_country.insert(0, self.focus_list.country)
        self.entry_focus_id.insert(0, self.focus_list.focus_id)
        self.category_list = category_list([category("FOCUS_FILTER_POLITICAL", "Political"), category("FOCUS_FILTER_RESEARCH", "Research"), category("FOCUS_FILTER_INDUSTRY", "Industry"), category("FOCUS_FILTER_STABILITY", "Stability"), category("FOCUS_FILTER_WAR_SUPPORT", "War Support"), category("FOCUS_FILTER_MANPOWER", "Manpower"), category("FOCUS_FILTER_FRA_POLITICAL_VIOLENCE", "Political Violence"), category("FOCUS_FILTER_FRA_OCCUPATION_COST", "Occupation Costs"), category("FOCUS_FILTER_ANNEXATION", "Territorial Expansion"), category("FOCUS_FILTER_CHI_INFLATION", "Inflation"), category("FOCUS_FILTER_USA_CONGRESS", "Congress"), category("FOCUS_FILTER_TFV_AUTONOMY", "Autonomy"), category("FOCUS_FILTER_MEX_CHURCH_AUTHORITY", "Church Authority"), category("FOCUS_FILTER_MEX_CAUDILLO_REBELLION", "Caudillo Rebellion"), category("FOCUS_FILTER_SPA_CIVIL_WAR", "Spanish Civil War"), category("FOCUS_FILTER_SPA_CARLIST_UPRISING", "Carlist Uprising"), category("FOCUS_FILTER_INTERNAL_AFFAIRS", "Internal Affairs"), category("FOCUS_FILTER_GRE_DEBT_TO_IFC", "Debt to the I.F.C."), category("FOCUS_FILTER_TUR_KURDISTAN", "Kurdistan"), category("FOCUS_FILTER_TUR_KEMALISM", "Kemalism"), category("FOCUS_FILTER_TUR_TRADITIONALISM", "Traditionalism"), category("FOCUS_FILTER_SOV_POLITICAL_PARANOIA", "Political Paranoia"), category("FOCUS_FILTER_PROPAGANDA", "Propaganda"), category("FOCUS_FILTER_ARMY_XP", "Army Experience"), category("FOCUS_FILTER_NAVY_XP", "Navy Experience"), category("FOCUS_FILTER_AIR_XP", "Air Experience"), category("FOCUS_FILTER_ITA_MISSIOLINI", "Mussolini's Missions"), category("FOCUS_FILTER_BALANCE_OF_POWER", "Balance of Power"), category("FOCUS_FILTER_SWI_MILITARY_READINESS", "Military Readiness")])

    def scr_to_pos(self, event_x = int, event_y = int):
        return int((event_x + (self.xbar.get()[0] * self.focus_list.width) - 25) / 50), int((event_y + (self.ybar.get()[0] * self.focus_list.height)) / 100)
    
    def submit(self):
        self.focus_list.country = self.entry_country.get()
        self.focus_list.focus_id = self.entry_focus_id.get()

    def shift_select(self, event):
        now_x, now_y = self.scr_to_pos(event.x, event.y)
        select = self.focus_list.exist(now_x, now_y)
        if self.focus_list.exist(now_x, now_y):
            if self.multi_select.exist(select):
                dele = int(self.multi_select.exist(select))
                self.multi_select.delete(select)
                self.canvas.delete(self.boxs[dele])
                self.boxs.remove(self.boxs[dele])
                return None
            self.multi = True
            self.multi_select.add(select)
            self.boxs.append(self.canvas.create_rectangle(10+50*now_x, 10+100*now_y, 90+50*now_x, 90+100*now_y, outline='Green'))

    def select_canvas(self,event):
        self.button_focus_edit.configure(state=DISABLED)
        self.label_error["text"] = ""
        if self.connecting or self.mutualling or self.moving or self.multi:
            return None
        self.select_x = self.scr_to_pos(event.x, event.y)[0]
        self.select_y = self.scr_to_pos(event.x, event.y)[1]
        self.rselect_data = self.focus_list.exist(self.select_x, self.select_y)
        self.canvas.moveto(self.select_rect, 50*self.select_x+10, 100*self.select_y+10)
        self.popup.entryconfig(0, state=NORMAL)
        self.popup.entryconfig(1, state=DISABLED)
        self.popup.entryconfig(2, state=DISABLED)
        self.popup.entryconfig(4, state=DISABLED)
        self.popup.entryconfig(5, state=DISABLED)
        self.popup.entryconfig(7, state=DISABLED)
        self.if_selected = False
        if self.focus_list.exist(self.select_x, self.select_y): 
            self.if_selected = True
            self.popup.entryconfig(0, state=DISABLED)
            self.popup.entryconfig(1, state=NORMAL)
            self.popup.entryconfig(2, state=NORMAL)
            self.popup.entryconfig(4, state=NORMAL)
            self.popup.entryconfig(5, state=NORMAL)
            self.popup.entryconfig(7, state=NORMAL)
        self.popup.post(event.x_root,event.y_root)

    def select_canvas2(self,event):
        self.lselect_x = self.scr_to_pos(event.x, event.y)[0]
        self.lselect_y = self.scr_to_pos(event.x, event.y)[1]
        self.lselect_data = self.focus_list.exist(self.lselect_x, self.lselect_y)
        self.canvas.moveto(self.select_rect, 50*self.lselect_x+10, 100*self.lselect_y+10)
        if self.multi:
            self.popup6.entryconfig(0, state=DISABLED)
            self.popup6.entryconfig(1, state=NORMAL)
            if self.focus_list.exist(self.lselect_x, self.lselect_y):
                self.multi_con = True
                self.popup6.entryconfig(0, state=NORMAL)
            self.popup6.post(event.x_root, event.y_root)
            return None

        if self.connecting:
            self.popup2.entryconfig(0, state=DISABLED)
            self.popup2.entryconfig(1, state=DISABLED)
            if self.focus_list.exist(self.lselect_x, self.lselect_y) and not self.lselect_data == self.rselect_data:
                if self.focus_list.serch_con(self.lselect_data, self.rselect_data) or self.focus_list.serch_con(self.rselect_data, self.lselect_data):
                    self.popup2.entryconfig(1, state=NORMAL)
                else:
                    self.popup2.entryconfig(0, state=NORMAL)
            self.popup2.post(event.x_root, event.y_root)
        if self.moving:
            self.popup3.entryconfig(0, state=DISABLED)
            if not self.focus_list.exist(self.lselect_x, self.lselect_y):  
                self.popup3.entryconfig(0, state=NORMAL)
            self.popup3.post(event.x_root, event.y_root)
        if self.mutualling:
            self.popup4.entryconfig(0, state=DISABLED, label = 'ここと排反')
            self.popup4.entryconfig(1, state=DISABLED)
            self.popup4.entryconfig(2, state=NORMAL)
            if self.focus_list.exist(self.lselect_x, self.lselect_y): 
                if self.focus_list.serch_mutu2(self.lselect_data, self.rselect_data):
                    self.popup4.entryconfig(1, state=NORMAL)
                else:
                    if self.lselect_y == self.select_y:
                        self.popup4.entryconfig(0, state=NORMAL)
                    else:
                        self.popup4.entryconfig(0, label = 'ここと排反(同じ列ですることを推奨)')
            self.popup4.post(event.x_root, event.y_root)
                
    def select_canvas3(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_canvas(self, event):
        self.canvas.scan_dragto(event.x, event.y)
        #dx = self.scr_to_pos(event.x, event.y)[0] - self.before_x
        #dy = self.scr_to_pos(event.x, event.y)[1] - self.before_y

    def new_focus(self):
        self.if_selected = True
        widgets = self.draw_focus(self.select_x, self.select_y, "focus." + str(self.focus_list.count))
        self.label_error["text"] = ""

        self.focus_list.add_focus(focus(widgets, self.focus_list.count, "focus_" + str(self.focus_list.count), self.select_x, self.select_y, 'GFX_focus_AST_never_gallipoli', 10, 'Political', ""))
        if self.focus_list.height <= (self.select_y + 1) * 100:
            self.focus_list.height += 200
        if self.focus_list.width <= (self.select_x + 2) * 50:
            self.focus_list.width += 200
        self.canvas.configure(scrollregion=(0, 0, self.focus_list.width, self.focus_list.height))
        self.canvas.update_idletasks()

    def draw_focus(self, x, y, name):
        oval = self.canvas.create_oval(50*x+20, 100*y+10, 50*x+80, 100*y+70)
        rect = self.canvas.create_rectangle(50*x+10, 100*y+50, 50*x+90, 100*y+80, fill="gray")
        text = self.canvas.create_text(50*x+50, 100*y+65, text = name)
        return [oval, rect, text]
        
    def remove_focus(self):
        self.canvas.delete(self.rselect_data.widgets[0])
        self.canvas.delete(self.rselect_data.widgets[1])
        self.canvas.delete(self.rselect_data.widgets[2])
        self.focus_list.remove(self.rselect_data, self.canvas)

    def edit_focus(self):
        self.button_focus_edit.configure(state=NORMAL)
        self.editing = self.rselect_data
        self.entry_focus_x.delete(0, END)
        self.entry_focus_y.delete(0, END)
        self.entry_focus_name.delete(0, END)
        self.entry_focus_cost.delete(0, END)
        self.entry_complete_reword.delete('1.0', END)
        self.entry_focus_x.insert(END, str(self.rselect_data.x))
        self.entry_focus_y.insert(END, str(self.rselect_data.y))
        self.entry_focus_name.insert(END, self.rselect_data.name)
        self.entry_focus_icon.set(self.rselect_data.icon)
        self.entry_focus_cost.insert(END, str(self.rselect_data.cost))
        self.entry_focus_category.set(self.rselect_data.category)
        self.entry_complete_reword.insert('1.0', str(self.rselect_data.complete_reword))

    def submit_focus(self):
        self.button_focus_edit.configure(state=DISABLED)
        self.editing.x = int(self.entry_focus_x.get())
        self.editing.y = int(self.entry_focus_y.get())
        self.editing.name = self.entry_focus_name.get()
        self.canvas.moveto(self.editing.widgets[0],self.editing.x*50+20, self.editing.y*100+10)
        self.canvas.moveto(self.editing.widgets[1],self.editing.x*50+10, self.editing.y*100+50)
        self.canvas.coords(self.editing.widgets[2],self.editing.x*50+50, self.editing.y*100+65)
        self.focus_list.move(self.editing.id, self.editing.x, self.editing.y, self.canvas)
        self.canvas.itemconfig(self.editing.widgets[2],text = self.entry_focus_name.get())
        self.editing.icon = self.entry_focus_icon.get()
        self.editing.cost = int(self.entry_focus_cost.get())
        self.editing.category = self.entry_focus_category.get()
        self.editing.complete_reword = self.entry_complete_reword.get('1.0', END)

    def move_focus(self):
        self.cancel()
        self.label_error["text"] = "左クリックで移動先を選ぶのだ"
        self.moving = True

    def moved_focus(self):
        self.moving = False
        self.canvas.moveto(self.rselect_data.widgets[0], self.lselect_x*50+20, self.lselect_y*100+10)
        self.canvas.moveto(self.rselect_data.widgets[1], self.lselect_x*50+10, self.lselect_y*100+50)
        self.canvas.coords(self.rselect_data.widgets[2], self.lselect_x*50+50, self.lselect_y*100+65)
        self.focus_list.move(self.rselect_data.id, self.lselect_x, self.lselect_y, self.canvas)

    def connect_focus(self):
        self.cancel()
        self.label_error["text"] = "左クリックで移動先を選ぶのだ"
        self.connecting = True

    def new_connect(self):
        self.connecting = False
        self.canvas.itemconfig(self.error_text, text = "")
        prev_data = self.rselect_data
        rear_data = self.lselect_data
        stick = self.canvas.create_line(self.select_x*50+50, self.select_y*100+50, self.select_x*50+50, self.select_y*100+100)
        stick2 = self.canvas.create_line(self.select_x*50+50, self.select_y*100+100, self.lselect_x*50+50, self.select_y*100+100)
        stick3 = self.canvas.create_line(self.lselect_x*50+50, self.select_y*100+100, self.lselect_x*50+50, self.lselect_y*100+50)
        self.canvas.lower(stick)
        self.canvas.lower(stick2)
        self.canvas.lower(stick3)
        sticks = [stick, stick2, stick3]
        self.focus_list.add_connect(connect(prev_data.id, rear_data.id, sticks))

    def delete_connect(self):
        connect_data = []
        self.connecting = False
        self.canvas.itemconfig(self.error_text, text = "")
        if self.focus_list.serch_con(self.lselect_data, self.rselect_data):
            connect_data = self.focus_list.serch_con(self.lselect_data, self.rselect_data)
        if self.focus_list.serch_con(self.rselect_data, self.lselect_data):
            connect_data = self.focus_list.serch_con(self.rselect_data, self.lselect_data)
        self.focus_list.remove_con(connect_data)
        self.canvas.delete(connect_data.widgets[0])
        self.canvas.delete(connect_data.widgets[1])
        self.canvas.delete(connect_data.widgets[2])

    def and_connect(self):
        connects = []
        datas = self.multi_select.all()
        for d in datas:
            stick = self.canvas.create_line(d.x*50+50, d.y*100+50, d.x*50+50, self.lselect_y*100, dash=(2,3))
            stick2 = self.canvas.create_line(d.x*50+50, self.lselect_y*100, self.lselect_x*50+50, self.lselect_y*100, dash=(2,3))
            stick3 = self.canvas.create_line(self.lselect_x*50+50, self.lselect_y*100, self.lselect_x*50+50, self.lselect_y*100+50, dash=(2,3))
            self.canvas.lower(stick)
            self.canvas.lower(stick2)
            self.canvas.lower(stick3)
            sticks = [stick, stick2, stick3]
            connects.append(connect(d.id, self.lselect_data.id, sticks))
        list = connect_list(connects, 'or', self.lselect_data.id)
        if list:
            self.focus_list.add_con_list(list)

    def cancel(self):
        self.if_selected = False
        self.multi_con = False
        self.multi_mov = False
        self.clear_select()
        self.connecting = False
        self.moving = False
        self.mutualling = False
        self.canvas.itemconfig(self.error_text, text = "")

    def clear_select(self):
        self.multi = False
        for w in reversed(self.boxs):
            self.canvas.delete(w)
        self.boxs = [self.canvas.create_rectangle(0,0,0,0)]
        self.multi_select.clear()
    
    def mutually_focus(self):
        self.cancel()
        self.label_error["text"] = "aaaa"
        self.mutualling = True

    def new_mutually(self):
        self.mutualling = False
        prev = self.rselect_data
        rear = self.lselect_data
        if self.lselect_x < self.select_x:
            stick = self.canvas.create_line(self.lselect_x*50+75, self.lselect_y*100+60, self.select_x*50+25, self.select_y*100+60, fill='indianRed4')
        else:
            stick = self.canvas.create_line(self.select_x*50+75, self.select_y*100+60, self.lselect_x*50+25, self.lselect_y*100+60, fill='indianRed4')
        self.canvas.lower(stick)
        sticks = [stick]
        self.focus_list.add_mutually(mutually(prev.id, rear.id, sticks))

    def delete_mutually(self):
        self.mutualling = False
        mutu_data = []
        mutu_data = self.focus_list.serch_mutu2(self.lselect_data, self.rselect_data)
        self.focus_list.remove_mutu(mutu_data)
        self.canvas.delete(mutu_data.widgets[0])

    def save_file(self):
        filename = filedialog.asksaveasfilename(title = "名前を付けて保存",filetypes = [("JSON形式", ".json")], # ファイルフィルタ 
        initialdir = "./", # 自分自身のディレクトリ
        defaultextension = "json"
        )
        if not filename:
            return None
        with open(filename, 'w') as f:
            f.write(json.dumps(asdict(self.focus_list)))
            f.close

    def open_file(self):
        filename = filedialog.askopenfilename(title = "開く",filetypes = [("JSON形式", ".json")], # ファイルフィルタ 
        initialdir = "./", # 自分自身のディレクトリ
        defaultextension = "json"
        )
        if not filename:
            return None
        self.focus_list.clear(self.canvas)
        self.entry_country.delete(0, END)
        self.entry_focus_id.delete(0, END)
        with open(filename, 'r') as f:
            json_file = json.load(f)
            self.focus_list = focus_list.from_dict(json_file)
            f.close
        self.focus_list.updata(self.canvas)
        self.entry_country.insert(END, self.focus_list.country)
        self.entry_focus_id.insert(END, self.focus_list.focus_id)
        self.connecting = False
        self.multi = False
        self.moving = False
        self.mutualling = False

    def export_file(self):
        filename = filedialog.asksaveasfilename(title = "出力",filetypes = [("テキスト", ".txt")], # ファイルフィルタ 
        initialdir = "./", # 自分自身のディレクトリ
        defaultextension = "txt"
        )
        with open(filename, mode='w', encoding='utf-8') as f:
            f.write(self.focus_list.export())
            f.close

    def export_loc_file(self):
        filename = filedialog.asksaveasfilename(title = "出力(言語ファイル)",filetypes = [("YML形式", ".yml")], # ファイルフィルタ 
        initialdir = "./", # 自分自身のディレクトリ
        defaultextension = "yml"
        )
        with open(filename, mode='w', encoding='utf-8-sig') as f:
            f.write(self.focus_list.l_export())
            f.close

    def close_display(self):
        quit()

@dataclass
class category():
    name : str
    id : str

@dataclass
class category_list():
    categories : list['category']

    def get(self, str:str):
        for cat in self.categories:
            if cat.name == str:
                return cat.id
        return None

@dataclass
class focus():
    widgets : list
    id : int
    name : str
    x : int
    y : int
    icon : str
    cost : int
    category : str
    complete_reword : str

@dataclass
class connect():
    prev : int
    rear : int
    widgets : list

@dataclass
class connect_list():
    connects : list['connect']
    type : str
    rear : int

@dataclass
class mutually():
    focus1 : int
    focus2 : int
    widgets : list

@dataclass
class multi_select():
    focuses : list['focus'] = None
    
    def add(self, focus:focus):
        self.focuses.append(focus)
        return None
    
    def delete(self, f:focus):
        self.focuses.remove(f)
        return None
    
    def exist(self, focus:focus):
        for i, f in enumerate(self.focuses):
            if f == focus:
                return i
        return None
    
    def clear(self):
        self.focuses = [focus([], -1, None, -1, -1, None, -1, None, None)]
        return None
    
    def all(self):
        return self.focuses[1:]

@dataclass
class focus_list(JSONWizard):
    country : str
    focus_id : str
    width : int
    height : int
    count : int
    focuses : list['focus'] = None
    connects : list['connect'] = None
    mutuallies : list['mutually'] = None
    connect_lists : list['connect_list'] = None

    def updata(self, canvas:Canvas):
        for focus in self.focuses:
            focus.widgets[0] = canvas.create_oval(50*focus.x+20, 100*focus.y+10, 50*focus.x+80, 100*focus.y+70)
            focus.widgets[1] = canvas.create_rectangle(50*focus.x+10, 100*focus.y+50, 50*focus.x+90, 100*focus.y+80, fill="gray")
            focus.widgets[2] = canvas.create_text(50*focus.x+50, 100*focus.y+65, text = focus.name)
        for connect in self.connects:
            prev = self.exist2(connect.prev)
            rear = self.exist2(connect.rear)
            if prev and rear:
                connect.widgets[0] = canvas.create_line(prev.x*50+50, prev.y*100+50, prev.x*50+50, prev.y*100+100)
                connect.widgets[1] = canvas.create_line(prev.x*50+50, prev.y*100+100, rear.x*50+50, prev.y*100+100)
                connect.widgets[2] = canvas.create_line(rear.x*50+50, prev.y*100+100, rear.x*50+50, rear.y*100+50)
                canvas.lower(connect.widgets[0])
                canvas.lower(connect.widgets[1])
                canvas.lower(connect.widgets[2])
        for mutually in self.mutuallies:
            focus1 = self.exist2(mutually.focus1)
            focus2 = self.exist2(mutually.focus2)
            if focus1 and focus2:
                if focus1.x < focus2.x:
                    mutually.widgets[0] = canvas.create_line(focus1.x*50+75, focus1.y*100+60, focus2.x*50+25, focus2.y*100+60, fill='indianRed4')
                else:
                    mutually.widgets[0] = canvas.create_line(focus2.x*50+75, focus2.y*100+60, focus1.x*50+25, focus1.y*100+60, fill='indianRed4')
                canvas.lower(mutually.widgets[0])
        for conlis in self.connect_lists:
            for con in conlis.connects:
                prev = self.exist2(con.prev)
                rear = self.exist2(con.rear)
                if prev and rear:
                    con.widgets[0] = canvas.create_line(prev.x*50+50, prev.y*100+50, prev.x*50+50, prev.y*100+100, dash=(2,3))
                    con.widgets[1] = canvas.create_line(prev.x*50+50, prev.y*100+100, rear.x*50+50, prev.y*100+100, dash=(2,3))
                    con.widgets[2] = canvas.create_line(rear.x*50+50, prev.y*100+100, rear.x*50+50, rear.y*100+50, dash=(2,3))
                    canvas.lower(con.widgets[0])
                    canvas.lower(con.widgets[1])
                    canvas.lower(con.widgets[2])
                

    def clear(self, canvas:Canvas):
        for focus in self.focuses:
            for wid in focus.widgets:
                canvas.delete(wid)
        for connect in self.connects:
            for wid in connect.widgets:
                canvas.delete(wid)
        for mutually in self.mutuallies:
            for wid in mutually.widgets:
                canvas.delete(wid)
        for conlis in self.connect_lists:
            for con in conlis.connects:
                for wid in con.widgets:
                    canvas.delete(wid)

    def add_focus(self, data:focus):
        self.focuses.append(data)
        self.count = 0
        while True:
            serch = True
            for id_list in self.focuses:
                if id_list.id == self.count:
                    serch = False
                    self.count += 1
                    break
            if serch:
                break

    def add_connect(self, data:connect):
        self.connects.append(data)

    def add_mutually(self, data:mutually):
        self.mutuallies.append(data)

    def add_con_list(self, data:connect_list):
        self.connect_lists.append(data)

    def exist(self, x:int, y:int):
        if self.focuses:
            for d in self.focuses:
                if x == d.x and y == d.y:
                    return d
        return None
    
    def exist2(self, id:int):
        if self.focuses:
            for d in self.focuses:
                if id == d.id:
                    return d
        return None
    
    def remove(self, data:focus, canvas:Canvas):
        self.focuses.remove(data)
        id = data.id
        connects = self.serch_con2(id)
        for d in reversed(connects):
            canvas.delete(d.widgets[0])
            canvas.delete(d.widgets[1])
            canvas.delete(d.widgets[2])
            self.connects.remove(d)
        mutuallies = self.serch_mutu(id)
        for d in reversed(mutuallies):
            canvas.delete(d.widgets[0])
            self.mutuallies.remove(d)
        conlis_rear = self.serch_cl_rear(id)
        for d in reversed(conlis_rear):
            for con in d.connects:
                canvas.delete(con.widgets[0])
                canvas.delete(con.widgets[1])
                canvas.delete(con.widgets[2])
            self.connect_lists.remove(d)
        conlis_prevs = self.serch_cl_prevs2(id)
        for d in reversed(conlis_prevs):
            for con in d.connects:
                canvas.delete(con.widgets[0])
                canvas.delete(con.widgets[1])
                canvas.delete(con.widgets[2])
            self.connect_lists.remove(d)
        return None
    
    def remove_con(self, data:connect):
        self.connects.remove(data)
        return None
    
    def remove_mutu(self, data:mutually):
        self.mutuallies.remove(data)
        return None
    
    def move(self, id:int, x:int, y:int, canvas:Canvas):
        move = self.exist2(id)
        move.x = x
        move.y = y
        if self.height <= (move.y + 1) * 100:
            self.height = (move.y + 1) * 100 + 200
        if self.width <= (move.x + 2) * 50:
            self.width = (move.x + 2) * 50 + 200
        canvas.configure(scrollregion=(0, 0, self.width, self.height))
        canvas.update_idletasks()
        for data in self.serch_con2(id):
            prev_data = self.exist2(data.prev) ;rear_data = self.exist2(data.rear)
            canvas.coords(data.widgets[0], prev_data.x*50+50, prev_data.y*100+50, prev_data.x*50+50, prev_data.y*100+100)
            canvas.coords(data.widgets[1], prev_data.x*50+50, prev_data.y*100+100, rear_data.x*50+50, prev_data.y*100+100)
            canvas.coords(data.widgets[2], rear_data.x*50+50, prev_data.y*100+100, rear_data.x*50+50, rear_data.y*100+50)
        for data2 in self.serch_cl_rear(id):
            for con in data2.connects:
                prev_data = self.exist2(con.prev) ;rear_data = self.exist2(con.rear)
                canvas.coords(con.widgets[0], prev_data.x*50+50, prev_data.y*100+50, prev_data.x*50+50, prev_data.y*100+100)
                canvas.coords(con.widgets[1], prev_data.x*50+50, prev_data.y*100+100, rear_data.x*50+50, prev_data.y*100+100)
                canvas.coords(con.widgets[2], rear_data.x*50+50, prev_data.y*100+100, rear_data.x*50+50, rear_data.y*100+50)
        for data3 in self.serch_cl_prevs(id):
            prev_data = self.exist2(data3.prev) ;rear_data = self.exist2(data3.rear)
            canvas.coords(data3.widgets[0], prev_data.x*50+50, prev_data.y*100+50, prev_data.x*50+50, prev_data.y*100+100)
            canvas.coords(data3.widgets[1], prev_data.x*50+50, prev_data.y*100+100, rear_data.x*50+50, prev_data.y*100+100)
            canvas.coords(data3.widgets[2], rear_data.x*50+50, prev_data.y*100+100, rear_data.x*50+50, rear_data.y*100+50)

    
    def serch_con(self, prev:focus, rear:focus):
        for data in self.connects:
            if prev.id == data.prev and rear.id == data.rear:
                return data
        return None
    
    def serch_con2(self, id:int):
        datas = []
        for data in self.connects:
            if id == data.prev or id == data.rear:
                datas.append(data)
        return datas
    
    def serch_mutu(self, id:int):
        datas = []
        for data in self.mutuallies:
            if id == data.focus1 or id == data.focus2:
                datas.append(data)
        return datas
    
    def serch_mutu2(self, focus1:focus, focus2:focus):
        for data in self.mutuallies:
            if data.focus1 == focus1.id and data.focus2 == focus2.id or data.focus2 == focus1.id and data.focus1 == focus2.id:
                return data
        return None
    
    def serch_cl_prevs(self, id:int):
        datas = []
        for conlis in self.connect_lists:
            for con in conlis.connects:
                if con.prev == id:
                    datas.append(con)
        return datas
    
    def serch_cl_prevs2(self, id:int):
        datas = []
        for conlis in self.connect_lists:
            for con in conlis.connects:
                if con.prev == id:
                    datas.append(conlis)
        return datas

    def serch_cl_rear(self, id:int):
        datas = []
        for conlis in self.connect_lists:
            if conlis.rear == id:
                datas.append(conlis)
        return datas
    
    def export(self):
        str = 'focus_tree = { \n\tid = %s\n\tcountry = {\n\t\tfactor = 0 \n\t\tmodifier = {\n\t\t\tadd = 10 \n\t\t\ttag = %s\n\t\t}\n\t} \n\tdefault = no' %(self.focus_id, self.country)
        for d in self.focuses:
            str += '\n\tfocus = {\n\t\tid = %s_%s \n\t\ticon = %s ' %(self.country, d.id, d.icon)
            if self.connects:
                for d2 in self.connects:
                    if d.id == d2.rear:
                        str += '\n\t\tprerequisite = { focus = %s_%s }' %(self.country, d2.prev)
            if self.connect_lists:
                for d2 in self.connect_lists:
                    if d.id == d2.rear:
                        str += '\n\t\tprerequisite = { '
                        for d3 in d2.connects:
                            str += 'focus = %s_%s ' %(self.country, d3.prev)
                        str += '}'
            if self.mutuallies:
                str += '\n\t\tmutually_exclusive = { '
                for d2 in self.mutuallies:
                    if d.id == d2.focus1:
                        str += 'focus = %s_%s ' %(self.country, d2.focus2)
                    if d.id == d2.focus2:
                        str += 'focus = %s_%s ' %(self.country, d2.focus1)
                str += '}'
            str += '\n\t\tx = %s \n\t\ty = %s \n\t\tcost = %s \n\t\tai_will_do = {} \n\t\tsearch_filters = {%s} \n\t\tcompletion_reward = { \n\t\t\t%s \n\t\t}\n\t}' %(d.x, d.y, d.cost, d.category, d.complete_reword)
        str += '\n}'
        return str
    
    def l_export(self):
        str = 'l_japanese:'
        for d in self.focuses:
            str += '\n %s_%s:0 "%s"' %(self.country, d.id, d.name)
        return str
        
        

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()