"""
Sistema de autocalificación para Taller de Lógica Difusa
Curso: Introducción a la Inteligencia Artificial - UNAL
Tema: Sistema Difuso de Satisfacción en una Cafetería

Para usar con GitHub Actions y GitHub Classroom
"""

import pytest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import sys
import os
import ast
import re

class NotebookTester:
    """Clase para probar notebooks de Lógica Difusa de forma estricta"""
    
    def __init__(self, notebook_path):
        self.notebook_path = notebook_path
        self.notebook = None
        self.executed_notebook = None
        self.namespace = {}
        
    def load_notebook(self):
        """Carga el notebook desde el archivo"""
        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                self.notebook = nbformat.read(f, as_version=4)
            return True
        except Exception as e:
            pytest.fail(f"❌ Error al cargar el notebook: {str(e)}")
            return False
    
    def execute_notebook(self, timeout=600):
        """
        Ejecuta el notebook completo para verificar que no tiene errores
        Este es el test más estricto - si algo falla, el test falla
        """
        try:
            ep = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
            self.executed_notebook, _ = ep.preprocess(
                self.notebook, 
                {'metadata': {'path': os.path.dirname(self.notebook_path) or '.'}}
            )
            return True
        except Exception as e:
            pytest.fail(f"❌ Error al ejecutar el notebook: {str(e)}\n\n"
                       f"💡 Asegúrate de que todas las celdas se ejecuten sin errores en Colab antes de subir.")
            return False
    
    def extract_code(self):
        """Extrae todo el código del notebook"""
        code_cells = [cell['source'] for cell in self.notebook.cells 
                     if cell['cell_type'] == 'code']
        return '\n\n'.join(code_cells)
    
    def get_variable_from_namespace(self, var_name):
        """Ejecuta el notebook y obtiene el valor de una variable"""
        if not self.executed_notebook:
            self.execute_notebook()
        
        code = self.extract_code()
        namespace = {}
        try:
            exec(code, namespace)
            return namespace.get(var_name, None)
        except Exception as e:
            pytest.fail(f"❌ Error al obtener la variable '{var_name}': {str(e)}")
            return None
    
    def check_variable_defined(self, var_name):
        """Verifica que una variable esté definida en el código"""
        code = self.extract_code()
        # Buscar definición de la variable
        pattern = rf'\b{re.escape(var_name)}\s*='
        return bool(re.search(pattern, code))
    
    def check_import_exists(self, module_name):
        """Verifica que un import específico exista"""
        code = self.extract_code()
        try:
            tree = ast.parse(code)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            return module_name in imports
        except SyntaxError as e:
            pytest.fail(f"❌ Error de sintaxis en el código: {str(e)}")
            return False
    
    def check_student_info_filled(self):
        """Verifica que el estudiante haya llenado su información"""
        code = self.extract_code()
        # Buscar las variables Nombre y Cédula
        nombre_match = re.search(r'Nombre\s*=\s*["\'](.+?)["\']', code)
        cedula_match = re.search(r'[CcÉé]dula\s*=\s*["\'](.+?)["\']', code)
        
        if not nombre_match or not cedula_match:
            return False
        
        nombre = nombre_match.group(1).strip()
        cedula = cedula_match.group(1).strip()
        
        # Verificar que no estén vacíos
        return len(nombre) > 1 and len(cedula) > 1


# Ruta al notebook del estudiante
NOTEBOOK_PATH = "Notebook/Taller_3.ipynb"

@pytest.fixture(scope="module")
def notebook():
    """Fixture que carga el notebook una vez para todos los tests"""
    tester = NotebookTester(NOTEBOOK_PATH)
    assert tester.load_notebook(), "No se pudo cargar el notebook"
    return tester


# ============================================================================
# TESTS ESPECÍFICOS PARA EL TALLER DE LÓGICA DIFUSA
# ============================================================================

def test_01_notebook_exists():
    """Test 1: Verifica que el notebook exista (3 puntos)"""
    assert os.path.exists(NOTEBOOK_PATH), \
        f"❌ El archivo {NOTEBOOK_PATH} no existe. Asegúrate de subir tu notebook con el nombre correcto."


def test_02_student_info_complete(notebook):
    """Test 2: Verifica que el estudiante haya completado su información (5 puntos)"""
    assert notebook.check_student_info_filled(), \
        "❌ Debes completar tu NOMBRE COMPLETO y CÉDULA en la primera celda del notebook."


def test_03_imports_necesarios(notebook):
    """Test 3: Verifica que se importen las librerías necesarias (5 puntos)"""
    required_imports = ['numpy', 'skfuzzy', 'matplotlib']
    
    for module in required_imports:
        assert notebook.check_import_exists(module), \
            f"❌ Falta el import de {module}. Necesitas: numpy, skfuzzy y matplotlib.pyplot"


def test_04_variables_entrada_definidas(notebook):
    """Test 4: Verifica que todas las variables de entrada estén definidas (10 puntos)"""
    variables_requeridas = [
        'calidad_cafe',
        'atencion_barista', 
        'rapidez_servicio',
        'satisfaccion'
    ]
    
    for var in variables_requeridas:
        assert notebook.check_variable_defined(var), \
            f"❌ La variable '{var}' no está definida. Revisa la sección de definición de variables."


def test_05_funciones_pertenencia_calidad_cafe(notebook):
    """Test 5: Verifica las funciones de pertenencia de calidad_cafe (8 puntos)"""
    code = notebook.extract_code()
    
    # Verificar que existan las etiquetas requeridas
    required_labels = ['mala', 'aceptable', 'excelente', 'muy_excelente']
    
    for label in required_labels:
        pattern = rf"calidad_cafe\['{label}'\]"
        assert re.search(pattern, code), \
            f"❌ Falta definir la función de pertenencia '{label}' para calidad_cafe"
    
    # Verificar que se use gaussiana para 'mala'
    assert 'fuzz.gaussmf' in code or 'fuzz.gmf' in code, \
        "❌ Debes usar una función gaussiana (gaussmf) para 'mala' en calidad_cafe"


def test_06_funciones_pertenencia_atencion_barista(notebook):
    """Test 6: Verifica las funciones de pertenencia de atencion_barista (8 puntos)"""
    code = notebook.extract_code()
    
    required_labels = ['deficiente', 'normal', 'mas_o_menos_normal', 'excelente']
    
    for label in required_labels:
        # Buscar variaciones en el nombre
        pattern = rf"atencion_barista\['({label}|{label.replace('_', ' ')}|{label.replace('mas_o_menos', 'más o menos')})'\]"
        assert re.search(pattern, code), \
            f"❌ Falta definir '{label}' para atencion_barista"


def test_07_funciones_pertenencia_rapidez_servicio(notebook):
    """Test 7: Verifica las funciones de pertenencia de rapidez_servicio (8 puntos)"""
    code = notebook.extract_code()
    
    required_labels = ['lenta', 'moderada', 'rapida']
    
    for label in required_labels:
        pattern = rf"rapidez_servicio\['{label}'\]"
        assert re.search(pattern, code), \
            f"❌ Falta definir '{label}' para rapidez_servicio"
    
    # Verificar que se use trapmf para 'lenta'
    assert 'fuzz.trapmf' in code, \
        "❌ Debes usar una función trapezoidal (trapmf) para 'lenta'"


def test_08_funciones_pertenencia_satisfaccion(notebook):
    """Test 8: Verifica las funciones de pertenencia de satisfaccion (salida) (8 puntos)"""
    code = notebook.extract_code()
    
    required_labels = ['baja', 'media', 'alta']
    
    for label in required_labels:
        pattern = rf"satisfaccion\['{label}'\]"
        assert re.search(pattern, code), \
            f"❌ Falta definir '{label}' para satisfaccion (variable de salida)"


def test_09_modificadores_difusos(notebook):
    """Test 9: Verifica que se apliquen modificadores difusos (concentración y dilatación) (8 puntos)"""
    code = notebook.extract_code()
    
    # Verificar función de concentración
    assert 'def concentracion' in code or 'def concentración' in code, \
        "❌ Falta definir la función 'concentracion' (elevar al cuadrado)"
    
    # Verificar que se use ** 2 para concentración
    assert '** 2' in code, \
        "❌ La concentración debe elevar al cuadrado (** 2)"
    
    # Verificar que se aplique concentración para 'muy_excelente'
    assert 'muy_excelente' in code or 'muy excelente' in code, \
        "❌ Falta aplicar concentración para crear 'muy_excelente'"


def test_10_reglas_definidas(notebook):
    """Test 10: Verifica que se definan las 7 reglas del sistema (10 puntos)"""
    code = notebook.extract_code()
    
    # Contar definiciones de reglas
    reglas_count = len(re.findall(r'regla\d+\s*=\s*ctrl\.Rule', code))
    
    assert reglas_count >= 7, \
        f"❌ Se esperan 7 reglas, pero solo se encontraron {reglas_count}. " \
        f"Debes definir regla1, regla2, ..., regla7"


def test_11_sistema_y_simulador_creados(notebook):
    """Test 11: Verifica que se creen el sistema y simulador (5 puntos)"""
    code = notebook.extract_code()
    
    assert 'ctrl.ControlSystem' in code, \
        "❌ Falta crear el sistema de control con ctrl.ControlSystem([reglas])"
    
    assert 'ctrl.ControlSystemSimulation' in code, \
        "❌ Falta crear el simulador con ctrl.ControlSystemSimulation(sistema)"


def test_12_valores_entrada_asignados(notebook):
    """Test 12: Verifica que se asignen valores a las entradas (5 puntos)"""
    code = notebook.extract_code()
    
    # Verificar que se asignen valores a las tres entradas
    entradas = ['calidad_cafe', 'atencion_barista', 'rapidez_servicio']
    
    for entrada in entradas:
        pattern = rf"simulador\.input\['{entrada}'\]\s*=\s*[\d.]+"
        assert re.search(pattern, code), \
            f"❌ Falta asignar un valor a simulador.input['{entrada}']"


def test_13_notebook_ejecuta_sin_errores(notebook):
    """Test 13: El notebook debe ejecutarse completamente sin errores (15 puntos)"""
    assert notebook.execute_notebook(), \
        "❌ El notebook tiene errores de ejecución. " \
        "Ejecuta todas las celdas en Colab y verifica que no haya errores antes de subir."


def test_14_calculo_satisfaccion_correcto(notebook):
    """Test 14: Verifica que se calcule la satisfacción correctamente (10 puntos)"""
    # Primero ejecutar el notebook
    assert notebook.execute_notebook(), "❌ El notebook no se puede ejecutar"
    
    # Obtener el valor de satisfacción
    code = notebook.extract_code()
    namespace = {}
    
    try:
        exec(code, namespace)
        
        # Verificar que exista el simulador
        assert 'simulador' in namespace, \
            "❌ La variable 'simulador' no está definida"
        
        simulador = namespace['simulador']
        
        # Verificar que se haya ejecutado compute()
        assert hasattr(simulador, 'output'), \
            "❌ No se ejecutó simulador.compute(). Debes calcular la salida del sistema."
        
        # Verificar que exista la salida de satisfacción
        assert 'satisfaccion' in simulador.output, \
            "❌ No se puede obtener la satisfacción. Verifica que el sistema esté bien configurado."
        
        satisfaccion_valor = simulador.output['satisfaccion']
        
        # Verificar que el valor esté en el rango esperado [0, 100]
        assert 0 <= satisfaccion_valor <= 100, \
            f"❌ La satisfacción debe estar entre 0 y 100, pero se obtuvo {satisfaccion_valor}"
        
        print(f"\n✅ Satisfacción calculada: {satisfaccion_valor:.2f}/100")
        
    except Exception as e:
        pytest.fail(f"❌ Error al calcular la satisfacción: {str(e)}")


def test_15_visualizaciones_incluidas(notebook):
    """Test 15: Verifica que se incluyan visualizaciones (5 puntos)"""
    code = notebook.extract_code()
    
    # Verificar que se use .view() o plt.plot
    assert '.view()' in code or 'plt.plot' in code, \
        "❌ Falta incluir visualizaciones. Usa .view() o matplotlib para graficar."
    
    # Verificar que se visualice al menos una variable
    visualizaciones = len(re.findall(r'\.view\(\)', code)) + len(re.findall(r'plt\.plot', code))
    
    assert visualizaciones >= 1, \
        "❌ Debes incluir al menos una visualización de las funciones de pertenencia o resultados."


# ============================================================================
# CONFIGURACIÓN DE PYTEST
# ============================================================================

if __name__ == "__main__":
    # Ejecutar los tests con pytest
    pytest.main([__file__, "-v", "--tb=short", "--color=yes"])
