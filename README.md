# 🤖 Basic Differential Drive Robot (ROS 2 + Gazebo Sim)

Este repositorio contiene la descripción y configuración de un robot diferencial básico para simulación usando **ROS 2** y **Gazebo Sim (Ignition / GZ)**. El proyecto soporta dos modos de control:

- Control nativo de Gazebo (GZ plugins)
- Control mediante ros2_control

---

## 📦 Estructura del repositorio

basic_dif_bot_description/
├── config/
├── launch/   
├── urdf/
├── worlds/

---

##  Cómo ejecutar la simulación

### 1. Compilar el workspace

```bash
colcon build
source install/setup.bash
```

---

### 2. Lanzar simulación con ros2_control

```bash
ros2 launch basic_dif_bot_description sim_gz_control.launch.py use_ros2_control:=true
```

---

### 3. Lanzar simulación con control nativo de Gazebo

```bash
ros2 launch basic_dif_bot_description sim_gz_pure.launch.py use_ros2_control:=false
```

---

## 🎮 Control del robot

### Teleoperación con teclado

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Cuando se usa ros2_control, el controlador espera:

geometry_msgs/msg/TwistStamped

Pero el teclado (teleop_twsit_keyboard) publica:

geometry_msgs/msg/Twist

---

## Solución: twist_stamper

```bash
ros2 run twist_stamper twist_stamper \
  --ros-args \
  -r cmd_vel_in:=/cmd_vel \
  -r cmd_vel_out:=/diff_drive_controller/cmd_vel
```

---


## 🔧 Controladores

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

---

## 📡 Topics importantes

### Comunes

- /cmd_vel
- /joint_states
- /tf
- /scan
- /imu
- /camera/*

---

### ros2_control

- /diff_drive_controller/cmd_vel
- /diff_drive_controller/odom

---

### Gazebo puro

- /odom (requiere bridge)

---

## 🔁 Bridges

Siempre activos:

- /clock
- /cmd_vel
- sensores

Condicional:

- /odom (solo sin ros2_control)

---

## ▶️ Iniciar simulación en PLAY

En launch:

```python
launch_arguments={'gz_args': ['-r ', world]}.items()
```

---

## 🧠 Nav2

Nav2 usa:

/cmd_vel (Twist)

Se necesita:

- twist_stamper (recomendado)

---

## 📌 Recomendaciones

- Usar ros2_control para integración con Nav2
- Usar GZ puro para pruebas rápidas

