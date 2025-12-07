import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Module 1 – ROS 2: Robotic Nervous System',
      collapsed: true,
      items: [
        'module-1-ros2/overview',
        'module-1-ros2/chapter-1-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 2 – Digital Twin (Gazebo & Unity)',
      collapsed: true,
      items: [
        'module-2-digital-twin-gazebo-unity/overview',
        'module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 3 – NVIDIA Isaac (AI-Robot Brain)',
      collapsed: true,
      items: [
        'module-3-nvidia-isaac/overview',
        'module-3-nvidia-isaac/chapter-1-getting-started',
      ],
    },
    {
      type: 'category',
      label: 'Module 4 – Vision-Language-Action (VLA)',
      collapsed: true,
      items: [
        'module-4-vision-language-action/overview',
        'module-4-vision-language-action/chapter-1-vla-intro',
      ],
    },
  ],
};

export default sidebars;
