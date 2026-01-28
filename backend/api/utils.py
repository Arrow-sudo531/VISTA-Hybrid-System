import pandas as pd
import io

def process_csv(file_obj):
    try:
        
        content = file_obj.read().decode('utf-8')
        
       
        if not content.strip():
            raise ValueError("The uploaded CSV file is empty.")

        df = pd.read_csv(io.StringIO(content), sep=',', on_bad_lines='skip')
        
       
        df.columns = df.columns.str.strip()

        
        averages = {
            "avg_flowrate": round(df['Flowrate'].mean(), 2) if 'Flowrate' in df.columns else 0,
            "avg_pressure": round(df['Pressure'].mean(), 2) if 'Pressure' in df.columns else 0,
            "avg_temp": round(df['Temperature'].mean(), 2) if 'Temperature' in df.columns else 0,
        }
        
        
        dist_col = 'Type' if 'Type' in df.columns else df.columns[1]
        distribution = df[dist_col].value_counts().to_dict()
        
        return {
            "total_count": len(df),
            "averages": averages,
            "distribution": distribution,
            "raw_data": df.head(10).to_dict(orient='records')
        }
    except Exception as e:
        
        raise Exception(f"CSV Processing Error: {str(e)}")