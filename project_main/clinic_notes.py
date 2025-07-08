
#  Copyright (c) 2025. Sandeep Chintabathina

# Code to map legacy provider comments into clinic_notes table

import pandas as pd

class Clinic_Notes:

    def __init__(self):
        self.df_clinic_notes = pd.read_csv('input/clinic_notes.csv',encoding='latin-1',na_filter=False)
        self.prepare_clinic_notes()

    # Allow chars between ascii 32(space) and 126(tilde) and eliminate others
    def remove_non_ascii(somestr:str):
        output=''
        for c in somestr:
            if ' ' <= c <= '~':
                output +=c
        return output

    @staticmethod
    def is_contained(df_set1, df_set2, key):
        # Check what elements of set2 are not in set 1
        codes = list(df_set1.loc[:, key])
        somelist = []
        for code in df_set2.loc[:, key]:
            if code not in codes:
                somelist.append(code)
        return somelist

    def prepare_clinic_notes(self):
        # Convert to lower case
        for col in self.df_clinic_notes.columns:
            self.df_clinic_notes.rename(columns={col:col.lower()},inplace=True)
        print('Initial num of clinic_note entries',len(self.df_clinic_notes))
        #print(self.df_clinic_notes.info())
        self.df_clinic_notes.loc[:,'note_text'] = [Clinic_Notes.remove_non_ascii(txt).strip() for txt in  self.df_clinic_notes.loc[:,'note_text']]

        #Drop rows where note_id and clinic_id are empty
        df_nulls = self.df_clinic_notes[self.df_clinic_notes['clinic_unique_id']=='']
        print('num of blank clinic ids',len(df_nulls))
        for idx in df_nulls.index:
            self.df_clinic_notes.drop(idx,axis=0,inplace=True)

        self.df_clinic_notes.reset_index(drop=True,inplace=True)

        # Compare clinics container and clinic notes container
        df_clinics = pd.read_csv('../clinics/clinics_in_container.csv',na_filter=False)
        df_clinics = df_clinics[['clinic_unique_id']]
        # Check if clinics in clinic notes are listed in clinics container
        somelist = Clinic_Notes.is_contained(df_clinics,self.df_clinic_notes,'clinic_unique_id')
        print('Clinics in clinic_notes but not in clinics',somelist)

        # Remove duplicates
        somelist= list(set(somelist))
        if len(somelist)>0:
            for id in somelist:
                print("Dropping",id,"from clinic_notes")
                df_clinic_notes_sub = self.df_clinic_notes[self.df_clinic_notes['clinic_unique_id']==id]
                # Drop every row matching index
                for idx in df_clinic_notes_sub.index:
                    self.df_clinic_notes.drop(idx, axis=0, inplace=True)
            self.df_clinic_notes.reset_index(drop=True, inplace=True)

        print("Final num of clinic_note entries",len(self.df_clinic_notes))

        # Take care of common_category_id, first strip it
        self.df_clinic_notes.loc[:,'common_category_id'] = [cat.strip() for cat in self.df_clinic_notes.loc[:,'common_category_id'] ]
        #Map it to corresponding code
        self.df_clinic_notes.loc[:,'common_category_id'] = [24 if cat=='SystemInfo' else 259 if cat=='VacProfile' else 0 for cat in self.df_clinic_notes.loc[:,'common_category_id']]

    def build_clinic_notes_csv(self):
        self.df_clinic_notes.to_csv('db_files/clinic_notes_bulk_insert.csv',index=False)
        print(len(self.df_clinic_notes),'clinic notes entries written to file')


