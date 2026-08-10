<div align="center">

# HONG-SON NGUYEN

### Robotics · Artificial Intelligence · Social Intelligence

**M.S. Researcher @ National Cheng Kung University (NCKU), Taiwan**  
**Networked Robotics & Systems Lab (NRSL)**

<br>

> **Building robots that understand people — not just obstacles.**

<br>

[![Portfolio](https://img.shields.io/badge/Interactive_Portfolio-9CFF6B?style=for-the-badge&logo=googlechrome&logoColor=071009)](https://sontypo.github.io)
[![GitHub](https://img.shields.io/badge/GitHub-sontypo-111820?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sontypo)
[![Google Scholar](https://img.shields.io/badge/Google_Scholar-PLACEHOLDER-4285F4?style=for-the-badge&logo=googlescholar&logoColor=white)](#)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-PLACEHOLDER-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](#)

</div>

---

## `01 // ABOUT_ME`

I am a robotics and AI researcher working on **human-aware autonomous navigation**, with a particular focus on how mobile robots can perceive, understand, predict, and safely interact with people in shared environments.

My research lies at the intersection of:

- **Social Robot Navigation**
- **Human–Robot Interaction**
- **Multi-Agent Trajectory Prediction**
- **Reinforcement Learning**
- **Human Motion & Interaction Modeling**
- **Robot Perception and Autonomous Systems**

I am especially interested in building representations that encode **human state, social structure, interaction dynamics, group behavior, motion uncertainty, and dynamic occupancy** for downstream planning and robot-learning policies.

My broader research question is:

> **How can an autonomous robot reason about people as dynamic social agents rather than treating them as moving obstacles?**

---

## `02 // CURRENT_RESEARCH`

```text
┌──────────────────────────────────────────────────────────────┐
│                    SOCIAL INTELLIGENCE STACK                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   PERCEPTION        HUMAN STATE       PREDICTION             │
│      │                  │                 │                   │
│      ▼                  ▼                 ▼                   │
│  RGB / LiDAR  →  {x, y, vx, vy}  →  FUTURE TRAJECTORIES     │
│                                             │                │
│                                             ▼                │
│                                     SOCIAL REASONING         │
│                                             │                │
│                                             ▼                │
│                                     NAVIGATION POLICY        │
│                                             │                │
│                                             ▼                │
│                                       MOBILE ROBOT           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### `R01 // Social Robot Navigation`

Designing navigation policies and planners that explicitly reason about:

`personal space` · `collision risk` · `TTC` · `clearance` · `human comfort` · `social interaction geometry`

---

### `R02 // Trajectory Prediction`

Developing multi-agent motion forecasting models using:

`dynamic interaction graphs` · `selective state-space models` · `Mamba / SSM` · `social structure` · `community-aware reasoning`

---

### `R03 // Robot Learning`

Training human-aware navigation behavior through:

`reinforcement learning` · `large-scale simulation` · `curriculum learning` · `reward shaping` · `simulation-to-real validation`

---

### `R04 // Human Interaction Modeling`

Exploring representations based on:

`human state` · `social force modeling` · `group behavior` · `LiDAR` · `dynamic occupancy` · `interaction-aware encoding`

---

## `03 // FEATURED_RESEARCH`

### Social Graph Mamba

**Structured State-Space Modeling for Social Trajectory Prediction**

An attention-free trajectory prediction framework that combines **dynamic interaction graphs** with **selective state-space models** for efficient multi-agent social reasoning.

```text
Dynamic Interaction Graph
          │
          ├── Ego-centric Scan
          ├── Goal-centric Scan
          ├── Community-aware Scan
          └── Global Interaction Scan
          │
          ▼
   Selective State-Space Model
          │
          ▼
  Multi-Modal Trajectory Prediction
```

`PyTorch` `Graph Learning` `Mamba / SSM` `ETH-UCY` `SDD`

---

### RL Social Navigation

Large-scale reinforcement-learning environments for human-aware navigation with:

- pedestrians and animated humans
- static and hybrid obstacle layouts
- configurable spawn distributions
- goal curriculum
- social-navigation rewards
- IsaacLab / RSL-RL training pipelines

`IsaacLab` `RSL-RL` `PPO` `ROS 2`

---

### Human Comfort in Robot–Pedestrian Encounters

Studying how robot behavior influences perceived pedestrian comfort through interaction variables such as:

- robot speed
- minimum distance
- lateral passing distance
- path curvature
- minimum TTC
- distance at minimum TTC

`HRI` `Human Subject Study` `TTC` `Clearance`

---

### Real-World Human-Aware Navigation

Physical robot experiments integrating perception, tracking, prediction, and navigation.

```text
Agilex Scout Mini
├── ZED-X Stereo Camera
├── Velodyne VLP-16 3D LiDAR
├── Jetson AGX Orin
└── ROS 2 Navigation / Human-Aware Control
```

---

## `04 // TECH_STACK`

### Robotics

![ROS2](https://img.shields.io/badge/ROS_2-22314E?style=flat-square&logo=ros&logoColor=white)
![Isaac Sim](https://img.shields.io/badge/Isaac_Sim-76B900?style=flat-square&logo=nvidia&logoColor=white)
![IsaacLab](https://img.shields.io/badge/IsaacLab-76B900?style=flat-square&logo=nvidia&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-F58113?style=flat-square&logo=gazebo&logoColor=white)
![Nav2](https://img.shields.io/badge/Nav2-111820?style=flat-square)

### AI / Machine Learning

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Reinforcement Learning](https://img.shields.io/badge/Reinforcement_Learning-111820?style=flat-square)
![Graph Learning](https://img.shields.io/badge/Graph_Learning-111820?style=flat-square)
![State Space Models](https://img.shields.io/badge/State_Space_Models-111820?style=flat-square)

### Development

![C++](https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=flat-square&logo=latex&logoColor=white)

---

## `05 // RESEARCH_PLATFORM`

```yaml
researcher:
  name: Hong-Son Nguyen
  affiliation: National Cheng Kung University
  laboratory: Networked Robotics & Systems Lab
  location: Tainan, Taiwan

research_focus:
  - social_robot_navigation
  - trajectory_prediction
  - reinforcement_learning
  - human_robot_interaction
  - human_interaction_modeling
  - human_aware_autonomy

robot_platform:
  mobile_base: Agilex Scout Mini
  camera: ZED-X
  lidar: Velodyne VLP-16
  compute: Jetson AGX Orin

software:
  - ROS 2
  - Isaac Sim
  - IsaacLab
  - RSL-RL
  - PyTorch
```

---

## `06 // SELECTED_PROJECTS`

| Project | Focus | Stack |
|---|---|---|
| **Social Graph Mamba** | Multi-agent trajectory prediction | PyTorch · Graph · SSM |
| **RL Social Navigation** | Human-aware policy learning | IsaacLab · RSL-RL · PPO |
| **Pedestrian Comfort Modeling** | Human–robot interaction | TTC · Clearance · Statistical Analysis |
| **Human-Aware Navigation System** | Real-world autonomous navigation | ROS 2 · ZED-X · VLP-16 |

> Repository links can be added here once the corresponding research code is public.

---

## `07 // GITHUB_ACTIVITY`

<div align="center">

<img height="165" src="https://github-readme-stats.vercel.app/api?username=sontypo&show_icons=true&hide_border=true&theme=github_dark&rank_icon=github" alt="Hong-Son's GitHub statistics" />

<img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=sontypo&layout=compact&hide_border=true&theme=github_dark" alt="Hong-Son's most used GitHub languages" />

</div>

---

## `08 // CONTACT_PROTOCOL`

```text
hongson@research:~$ whoami

Hong-Son Nguyen
Robotics / Artificial Intelligence / Human-Aware Autonomy

hongson@research:~$ status

OPEN_TO:
  research collaboration
  robotics / AI opportunities
  academic discussion
  PhD opportunities

hongson@research:~$ connect
```

<div align="center">

[![Portfolio](https://img.shields.io/badge/PORTFOLIO-sontypo.github.io-9CFF6B?style=for-the-badge&logoColor=071009)](https://sontypo.github.io)
[![Email](https://img.shields.io/badge/EMAIL-ADD_EMAIL-111820?style=for-the-badge&logo=gmail&logoColor=white)](#)
[![Scholar](https://img.shields.io/badge/SCHOLAR-ADD_LINK-4285F4?style=for-the-badge&logo=googlescholar&logoColor=white)](#)
[![LinkedIn](https://img.shields.io/badge/LINKEDIN-ADD_LINK-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](#)

<br>

`SOCIAL NAVIGATION` · `ROBOT LEARNING` · `HUMAN MOTION INTELLIGENCE`

</div>
