from flask import Flask, request, send_file, jsonify
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
import io

app = Flask(__name__)

@app.route('/stakeholder-venn', methods=['POST'])
def generate_stakeholder_venn():
    try:
        data = request.json
        categorias = data['categorias']
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(18, 14))
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Parámetros de los círculos
        radius = 3.5
        center_x = 8
        center_y = 7
        separation = 3.2  # Mayor separación entre círculos
        
        # Centros de los 3 círculos (más separados)
        # Poder (arriba izquierda)
        circle1_center = (center_x - separation*0.866, center_y + separation*0.5)
        # Legitimidad (arriba derecha)  
        circle2_center = (center_x + separation*0.866, center_y + separation*0.5)
        # Urgencia (abajo centro)
        circle3_center = (center_x, center_y - separation)
        
        # Colores diferentes para cada círculo (suaves)
        color_poder = '#ffcccc'      # Rojo suave
        color_legitimidad = '#ccccff' # Azul suave
        color_urgencia = '#ccffcc'    # Verde suave
        
        # Dibujar los círculos
        circle1 = Circle(circle1_center, radius, fill=True, facecolor=color_poder, 
                        edgecolor='darkred', linewidth=2.5, alpha=0.5, zorder=1)
        circle2 = Circle(circle2_center, radius, fill=True, facecolor=color_legitimidad, 
                        edgecolor='darkblue', linewidth=2.5, alpha=0.5, zorder=1)
        circle3 = Circle(circle3_center, radius, fill=True, facecolor=color_urgencia, 
                        edgecolor='darkgreen', linewidth=2.5, alpha=0.5, zorder=1)
        
        ax.add_patch(circle1)
        ax.add_patch(circle2)
        ax.add_patch(circle3)
        
        # Etiquetas de los conjuntos (más alejadas)
        ax.text(circle1_center[0] - 3.2, circle1_center[1] + 2.2, 'Poder', 
               fontsize=16, fontweight='bold', ha='center')
        ax.text(circle2_center[0] + 3.2, circle2_center[1] + 2.2, 'Legitimidad', 
               fontsize=16, fontweight='bold', ha='center')
        ax.text(circle3_center[0], circle3_center[1] - 4.2, 'Urgencia', 
               fontsize=16, fontweight='bold', ha='center')
        
        # Función para formatear nombres
        def format_names(names, num, max_names=5):
            if len(names) == 0:
                return f"{num}"
            if len(names) <= max_names:
                return f"{num}\n" + '\n'.join(names)
            shown = '\n'.join(names[:max_names])
            return f"{num}\n{shown}\n(+{len(names) - max_names} más)"
        
        # Posiciones ajustadas para los segmentos (más separados)
        positions = {
            # 1 - Solo Poder (izquierda superior)
            'inactivo': (circle1_center[0] - 1.8, circle1_center[1] + 1.0),
            
            # 2 - Solo Legitimidad (derecha superior)
            'discrecional': (circle2_center[0] + 1.8, circle2_center[1] + 1.0),
            
            # 3 - Solo Urgencia (abajo centro)
            'demandante': (circle3_center[0], circle3_center[1] - 1.8),
            
            # 4 - Poder + Legitimidad (centro arriba)
            'dominante': (center_x, center_y + 2.5),
            
            # 5 - Poder + Urgencia (izquierda abajo)
            'peligroso': (circle1_center[0] - 0.5, center_y - 0.3),
            
            # 6 - Legitimidad + Urgencia (derecha abajo)
            'dependiente': (circle2_center[0] + 0.5, center_y - 0.3),
            
            # 7 - Los tres (centro exacto)
            'criticos': (center_x, center_y + 0.3)
        }
        
        # Añadir texto en cada segmento
        segments = [
            ('inactivo', '1', categorias['inactivo']),
            ('discrecional', '2', categorias['discrecional']),
            ('demandante', '3', categorias['demandante']),
            ('dominante', '4', categorias['dominante']),
            ('peligroso', '5', categorias['peligroso']),
            ('dependiente', '6', categorias['dependiente']),
            ('criticos', '7', categorias['criticos'])
        ]
        
        for segment_name, num, names in segments:
            pos = positions[segment_name]
            text = format_names(names, num, 4)
            ax.text(pos[0], pos[1], text, fontsize=10, fontweight='bold', 
                   ha='center', va='center', zorder=2,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           alpha=0.8, edgecolor='gray', linewidth=0.5))
        
        # Añadir leyenda en un recuadro
        legend_text = (
            "Categorías:\n"
            "1: Inactivo - baja\n"
            "2: Discrecional - baja\n"
            "3: Demandante - baja\n"
            "4: Dominante - media\n"
            "5: Peligroso - media\n"
            "6: Dependiente - media\n"
            "7: Críticos - alta"
        )
        
        ax.text(14.5, center_y, legend_text, fontsize=12, 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, 
                        edgecolor='black', linewidth=1),
               verticalalignment='center')
        
        # Título
        ax.text(center_x, 13, 'Análisis de Preponderancia de Stakeholders', 
               fontsize=20, fontweight='bold', ha='center')
        
        # Ajustar límites
        ax.set_xlim(0, 18)
        ax.set_ylim(0, 14)
        
        # Guardar imagen
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Servicio activo',
        'endpoint': '/stakeholder-venn',
        'method': 'POST'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

