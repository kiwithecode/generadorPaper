import openai
import json
import os
import PyPDF2

# Establece tu clave de API de OpenAI
openai.api_key = 'TU_CLAVE_DE_API'  # Reemplaza con tu clave real

def analizar_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        texto = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            texto += page.extract_text()
    return texto

def clasificar_articulo(articulo_texto):
    silueta_keywords = ["forma", "contorno", "perfil", "silueta"]
    textura_keywords = ["textura", "superficie", "granularidad"]
    color_keywords = ["color", "tonalidad", "matiz", "cromático"]
    
    silueta_score = sum(articulo_texto.lower().count(word) for word in silueta_keywords)
    textura_score = sum(articulo_texto.lower().count(word) for word in textura_keywords)
    color_score = sum(articulo_texto.lower().count(word) for word in color_keywords)
    
    max_score = max(silueta_score, textura_score, color_score)
    
    if max_score == silueta_score:
        return "silueta"
    elif max_score == textura_score:
        return "textura"
    elif max_score == color_score:
        return "color"
    else:
        return "indeterminado"

def analizar_articulo(articulo_texto):
    prompts = {
        "title": "Extrae el título del siguiente artículo científico:\n\n" + articulo_texto,
        "abstract": "Extrae el resumen del siguiente artículo científico:\n\n" + articulo_texto,
        "introduction": "Extrae la introducción del siguiente artículo científico:\n\n" + articulo_texto,
        "methodology": "Extrae la metodología del siguiente artículo científico:\n\n" + articulo_texto,
        "results": "Extrae los resultados del siguiente artículo científico:\n\n" + articulo_texto,
        "discussion": "Extrae la discusión del siguiente artículo científico:\n\n" + articulo_texto,
        "conclusion": "Extrae la conclusión del siguiente artículo científico:\n\n" + articulo_texto,
        "references": "Extrae las referencias del siguiente artículo científico:\n\n" + articulo_texto
    }

    article_data = {}
    
    for section, prompt in prompts.items():
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Utiliza el modelo adecuado
            messages=[
                {"role": "system", "content": "Eres un asistente útil y servicial."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        article_data[section] = response.choices[0].message['content'].strip()
    
    # Procesar las referencias como una lista
    article_data['references'] = article_data['references'].split('\n')
    
    # Clasificación del artículo
    article_data['classification'] = clasificar_articulo(articulo_texto)
    
    return article_data

def analizar_pdfs_en_carpeta(carpeta):
    articulos = []
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.pdf'):
            pdf_path = os.path.join(carpeta, archivo)
            texto = analizar_pdf(pdf_path)
            articulo_data = analizar_articulo(texto)
            articulos.append(articulo_data)
    return articulos

def main():
    # Ruta a la carpeta que contiene los archivos PDF (ruta relativa)
    carpeta_pdfs = os.path.join('data', 'input_pdfs')
    
    # Verificar si la carpeta de PDFs existe
    if not os.path.exists(carpeta_pdfs):
        print(f"La carpeta de PDFs no existe: {carpeta_pdfs}")
        return

    # Análisis de los PDFs en la carpeta
    articulos = analizar_pdfs_en_carpeta(carpeta_pdfs)
    
    # Ruta para guardar el JSON generado
    carpeta_salida = os.path.join('data', 'output_jsons')
    os.makedirs(carpeta_salida, exist_ok=True)
    output_json_path = os.path.join(carpeta_salida, 'articulos_analizados.json')
    
    # Guardar el JSON en un archivo
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(articulos, json_file, indent=4, ensure_ascii=False)
    
    print(f"JSON 'articulos_analizados.json' generado y guardado en {output_json_path}.")

if __name__ == '__main__':
    main()
