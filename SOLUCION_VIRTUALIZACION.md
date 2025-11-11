# 🔧 SOLUCIÓN: Habilitar Virtualización para Docker

## ❌ PROBLEMA DETECTADO

Tu sistema muestra:
- **Procesador**: AMD Ryzen 7 5700 ✅ (Soporta virtualización)
- **Virtualización en BIOS**: ❌ DESHABILITADA
- **Hyper-V**: ❌ NO PRESENTE
- **Docker Desktop**: ❌ NO PUEDE INICIAR

---

## ✅ SOLUCIÓN PASO A PASO

### **PASO 1: Habilitar AMD-V en BIOS** (5 minutos)

Tu procesador AMD Ryzen necesita que habilites **SVM Mode** (AMD Virtualization) en BIOS:

#### 1.1 Reiniciar y Entrar a BIOS

1. **Reinicia tu PC**
2. Apenas inicie, **presiona repetidamente** una de estas teclas:
   - `Del` (Delete) - Más común en AMD
   - `F2`
   - `F10`
   - `F12`
   - Depende de tu motherboard (MSI, ASUS, Gigabyte, etc.)

3. Si aparece el logo de Windows, reinicia de nuevo y prueba otra tecla

#### 1.2 Buscar la Opción de Virtualización

Dependiendo de tu motherboard, busca en:

**Opción A - ASUS**:
```
Advanced Mode (F7) 
  → Advanced 
    → CPU Configuration 
      → SVM Mode: [Disabled] → Cambiar a [Enabled]
```

**Opción B - MSI**:
```
OC (Overclocking)
  → CPU Features
    → SVM Mode: [Disabled] → Cambiar a [Enabled]
```

**Opción C - Gigabyte**:
```
M.I.T (Tweaker)
  → Advanced CPU Settings
    → SVM Mode: [Disabled] → Cambiar a [Enabled]
```

**Opción D - ASRock**:
```
Advanced
  → CPU Configuration
    → AMD-V: [Disabled] → Cambiar a [Enabled]
```

La opción puede llamarse:
- **SVM Mode**
- **AMD-V**
- **AMD Virtualization**
- **Secure Virtual Machine**

#### 1.3 Guardar y Salir

1. Presiona `F10` (o busca "Save & Exit")
2. Confirma "Yes"
3. Tu PC se reiniciará

---

### **PASO 2: Habilitar Características de Windows** (10 minutos)

Después de reiniciar con BIOS configurado:

#### 2.1 Ejecutar Script Automático

1. **Abre PowerShell como ADMINISTRADOR**:
   - Busca "PowerShell" en el menú inicio
   - Click derecho → "Ejecutar como administrador"
   - Debe decir "Administrador" en el título de la ventana

2. **Navega al proyecto**:
   ```powershell
   cd "D:\TEC\Sistemas Operativos\Proyecto2-SO-Multimedia-Distribuido"
   ```

3. **Ejecuta el script**:
   ```powershell
   .\habilitar-virtualizacion.ps1
   ```

4. **El script hará**:
   - ✅ Habilitar Hyper-V
   - ✅ Habilitar Plataforma de Máquina Virtual
   - ✅ Habilitar WSL 2
   - ✅ Te preguntará si deseas reiniciar

#### 2.2 Opción Manual (Si el script falla)

Ejecuta estos comandos UNO POR UNO en PowerShell (como Admin):

```powershell
# Habilitar Plataforma de Máquina Virtual
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Habilitar WSL 2
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Habilitar Hyper-V (solo Windows Pro/Enterprise)
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart

# Reiniciar
Restart-Computer
```

---

### **PASO 3: Verificar y Configurar Docker** (5 minutos)

Después del segundo reinicio:

#### 3.1 Verificar Virtualización

Abre PowerShell normal y ejecuta:

```powershell
Get-ComputerInfo | Select-Object HyperVisorPresent, HyperVRequirementVirtualizationFirmwareEnabled
```

**Debe mostrar**:
```
HyperVisorPresent : True
HyperVRequirementVirtualizationFirmwareEnabled : True
```

#### 3.2 Iniciar Docker Desktop

1. Busca "Docker Desktop" en el menú inicio
2. Ábrelo
3. Espera 1-2 minutos
4. Debería iniciar sin errores

#### 3.3 Configurar Docker para WSL 2

Si Docker pide elegir backend:
1. Settings (⚙️) → General
2. ✅ Marca "Use the WSL 2 based engine"
3. Apply & Restart

#### 3.4 Verificar Funcionamiento

En PowerShell:

```powershell
docker --version
docker compose version
docker run hello-world
```

Deberías ver:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## 🆘 SI AÚN NO FUNCIONA

### Problema 1: "No puedo entrar a BIOS"

**Solución - Método Alternativo**:

1. En Windows, ve a: Configuración → Actualización y seguridad → Recuperación
2. En "Inicio avanzado", click "Reiniciar ahora"
3. Solucionar problemas → Opciones avanzadas → Configuración de firmware UEFI
4. Click "Reiniciar"
5. Entrará automáticamente a BIOS

### Problema 2: "No encuentro la opción SVM en BIOS"

Busca también:
- `Advanced CPU Core Features`
- `CPU Advanced Features`
- `Secure Virtual Machine Mode`
- Revisa TODAS las pestañas de BIOS
- Actualiza BIOS a la última versión (descarga del sitio del fabricante)

### Problema 3: "Tengo Windows Home"

Windows Home NO soporta Hyper-V, pero SÍ soporta WSL 2:

1. Asegúrate de que BIOS tenga SVM habilitado
2. En Docker Desktop Settings:
   - General → "Use WSL 2 based engine" ✅
3. Instala WSL 2:
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```

### Problema 4: "Error 0x80370102 en Docker"

```powershell
# Deshabilitar Hyper-V temporalmente
bcdedit /set hypervisorlaunchtype off
# Reiniciar
Restart-Computer

# Después de reiniciar, volver a habilitar
bcdedit /set hypervisorlaunchtype auto
Restart-Computer
```

---

## ✅ CHECKLIST COMPLETO

- [ ] **PASO 1**: Reiniciar PC y entrar a BIOS
- [ ] **PASO 1**: Encontrar opción SVM Mode / AMD-V
- [ ] **PASO 1**: Cambiar a "Enabled"
- [ ] **PASO 1**: Guardar (F10) y reiniciar
- [ ] **PASO 2**: Abrir PowerShell como ADMIN
- [ ] **PASO 2**: Ejecutar `.\habilitar-virtualizacion.ps1`
- [ ] **PASO 2**: Reiniciar PC (segunda vez)
- [ ] **PASO 3**: Verificar virtualización está "True"
- [ ] **PASO 3**: Abrir Docker Desktop
- [ ] **PASO 3**: Docker inicia sin errores
- [ ] **PASO 3**: `docker run hello-world` funciona

---

## 🎯 DESPUÉS DE ESTO

Una vez Docker funcione:

```powershell
cd "D:\TEC\Sistemas Operativos\Proyecto2-SO-Multimedia-Distribuido"
docker compose build
docker compose up -d
```

Y tu sistema distribuido estará corriendo! 🚀

---

## 📞 AYUDA ADICIONAL

**Videos útiles** (YouTube):
- "How to enable AMD-V in BIOS"
- "Enable virtualization AMD Ryzen"
- "Docker Desktop WSL 2 setup Windows"

**Si nada funciona**:
- Verifica que Windows esté actualizado
- Actualiza BIOS a última versión
- Desinstala y reinstala Docker Desktop
- Revisa que antivirus no bloquee virtualización

---

**Última actualización**: 10 de noviembre de 2025

**Tu configuración detectada**:
- Procesador: AMD Ryzen 7 5700 ✅
- Virtualización BIOS: ❌ DESHABILITADA (arreglar primero)
- Hyper-V: ❌ NO PRESENTE (arreglar después de BIOS)
