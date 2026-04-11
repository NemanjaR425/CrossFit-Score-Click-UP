def get_all_results():
    try:
        ref = db.reference('competitions')
        all_data = ref.get()
        
        results = []
        if all_data:
            # Provjeravamo da li je all_data lista (često kod numeričkih ključeva)
            if isinstance(all_data, list):
                # Ako je lista, koristimo enumerate da dobijemo "indeks" kao ime WOD-a
                for wod_idx, athletes in enumerate(all_data):
                    if athletes:  # Preskačemo prazne slotove u listi
                        # Ponovo provjeravamo nivo atleta (može biti lista ili dict)
                        athlete_items = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                        for athlete_id, details in athlete_items:
                            if details:
                                results.append({
                                    "Takmičar": details.get('name', f'ID: {athlete_id}'),
                                    "WOD": f"WOD {wod_idx}",
                                    "Ponavljanja": details.get('reps', 0)
                                })
            
            # Ako je all_data standardni rečnik (dict)
            elif isinstance(all_data, dict):
                for wod_name, athletes in all_data.items():
                    if athletes:
                        athlete_items = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                        for athlete_id, details in athlete_items:
                            if details:
                                results.append({
                                    "Takmičar": details.get('name', 'Nepoznato'),
                                    "WOD": wod_name.replace("_", " "),
                                    "Ponavljanja": details.get('reps', 0)
                                })
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            # Sabiramo ponavljanja po imenu takmičara
            summary = df.groupby("Takmičar")["Ponavljanja"].sum().reset_index()
            # Sortiramo od najvišeg ka najnižem
            summary = summary.sort_values(by="Ponavljanja", ascending=False).reset_index(drop=True)
            # Dodajemo kolonu za Rang
            summary.insert(0, "Rang", range(1, len(summary) + 1))
            return summary
            
        return pd.DataFrame(columns=["Rang", "Takmičar", "Ponavljanja"])
        
    except Exception as e:
        st.error(f"Greška u obradi podataka: {e}")
        return pd.DataFrame()
