# ⚡ Quick Start - Revisión de Código (5 minutos)

## Para el Ingeniero de Software que Revisará el Código

### 🚀 Inicio Rápido

```bash
# 1. Clonar y entrar al proyecto
git clone https://github.com/Jose061125/ips2.git
cd ips2

# 2. Crear entorno virtual
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar tests
pytest -v

# Esperado: ✅ 16 tests pasando

# 5. Ejecutar aplicación
python run.py

# 6. Abrir navegador
# http://127.0.0.1:5000
```

---

## 📋 Checklist Express (30 min)

### ✅ Tests Automatizados (5 min)
```bash
pytest -v --cov=app --cov-report=term
```
- [ ] 16/16 tests pasando
- [ ] Cobertura >70%

### ✅ Análisis de Seguridad (5 min)
```bash
pip install bandit
bandit -r app/ -ll
```
- [ ] 0 issues de severidad HIGH

### ✅ Linting (5 min)
```bash
pip install flake8
flake8 app/ --max-line-length=120 --exclude=__pycache__
```
- [ ] Sin errores críticos

### ✅ Pruebas Manuales (15 min)

1. **Registro y Login** (3 min)
   - Registrar usuario: `test_admin` / `Test@1234` / rol: admin
   - Login exitoso
   - Verificar dashboard

2. **RBAC** (3 min)
   - Crear usuario no-admin
   - Intentar acceder `/admin/users`
   - Verificar error 403

3. **CRUD Pacientes** (5 min)
   - Crear paciente: "Juan Pérez" / "123456789"
   - Editar paciente
   - Ver lista

4. **Rate Limiting** (2 min)
   - 5 intentos fallidos de login
   - Verificar bloqueo de cuenta

5. **Logs de Auditoría** (2 min)
   ```bash
   cat logs/audit.log
   ```
   - [ ] Eventos registrados (login, accesos denegados)

---

## 🎯 Áreas Críticas a Revisar

### 🔴 Prioridad Alta (Revisar PRIMERO)

1. **`app/auth/routes.py`** - Autenticación
   - ¿Contraseñas hasheadas?
   - ¿CSRF protection?
   - ¿Rate limiting?

2. **`app/infrastructure/security/`** - Control de acceso
   - ¿RBAC implementado?
   - ¿Decoradores `@require_role()`?

3. **`app/services/`** - Lógica de negocio
   - ¿Separación de responsabilidades?
   - ¿Depende de puertos (abstracciones)?

4. **`config.py`** - Configuración
   - ¿SECRET_KEY segura?
   - ¿Variables de entorno?

5. **`tests/`** - Calidad de tests
   - ¿Cobertura suficiente?
   - ¿Tests de seguridad?

---

## 📊 Métricas Esperadas

| Métrica | Valor Esperado | Cómo Verificar |
|---------|----------------|----------------|
| **Tests pasando** | 16/16 | `pytest -v` |
| **Cobertura** | >70% | `pytest --cov=app` |
| **Issues Bandit** | 0 HIGH | `bandit -r app/ -ll` |
| **Tiempo de carga** | <3s | Navegador (Network tab) |
| **Líneas de código** | ~3,500 | `cloc app/` |

---

## 🔍 Preguntas Clave

**Arquitectura:**
- ¿Se ve clara la separación hexagonal (domain/services/adapters)?

**Seguridad:**
- ¿Puedo acceder a rutas de admin sin ser admin?
- ¿Las contraseñas están en texto plano en la DB?

**Calidad:**
- ¿El código es legible y bien organizado?
- ¿Hay código duplicado evidente?

**Funcionalidad:**
- ¿Funcionan los flujos principales (registro, login, CRUD)?

---

## 📖 Documentación Completa

Para revisión exhaustiva, ver: **`docs/GUIA_REVISION_CODIGO.md`**

Incluye:
- 19 tests detallados paso a paso
- Checklist completo de revisión
- Escenarios de uso end-to-end
- Formato de reporte
- Herramientas recomendadas

---

## 🆘 Problemas Comunes

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "No module named 'app'"
```bash
# Asegúrate de estar en el directorio raíz
cd ips-main
```

### Tests fallan
```bash
# Eliminar instancia anterior
rm -rf instance/
python run.py  # Recrear DB
pytest -v
```

### Puerto 5000 ocupado
```bash
# En run.py cambiar a:
app.run(debug=True, port=5001)
```

---

## 📞 Contacto

**Desarrollador:** Jose Luis  
**Repo:** https://github.com/Jose061125/ips2  
**Tiempo estimado de revisión:** 4-6 horas  

---

**¡Éxito en tu revisión! 🚀**
