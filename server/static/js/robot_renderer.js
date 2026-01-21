/**
 * GO2 Robot 3D Renderer with Gaussian Splatting
 * Renders GO2 quadruped robot using Three.js with OBJ meshes
 */

import * as THREE from 'three';
import { SplatMesh } from '@sparkjsdev/spark';

class RobotRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;

        this.bodyMeshes = {};
        this.robotGroup = null;
        this.objLoader = new window.THREE.OBJLoader();

        this.isLoading = true;
        this.loadedMeshCount = 0;
        this.totalMeshCount = 0;

        // GO2 body list (from MuJoCo XML)
        this.bodyList = ['base_link', 'FL_hip', 'FL_thigh', 'FL_calf', 'FR_hip', 'FR_thigh', 'FR_calf',
                         'RL_hip', 'RL_thigh', 'RL_calf', 'RR_hip', 'RR_thigh', 'RR_calf'];

        this.initScene();
        this.setupLights();
        this.setupGround();
        this.animate();
    }

    initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);

        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
        this.camera.position.set(2, 1.5, 2);
        this.camera.lookAt(0, 0.3, 0);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.container.appendChild(this.renderer.domElement);

        this.controls = new window.THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.target.set(0, 0.3, 0);
        this.controls.update();

        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 5);
        dirLight.castShadow = true;
        this.scene.add(dirLight);

        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
        hemiLight.position.set(0, 20, 0);
        this.scene.add(hemiLight);
    }

    setupGround() {
        // Ground plane (commented out - using Gaussian Splatting environment instead)
        // const groundGeometry = new THREE.PlaneGeometry(20, 20);
        // const groundMaterial = new THREE.MeshStandardMaterial({
        //     color: 0x16213e,
        //     roughness: 0.8,
        //     metalness: 0.2
        // });
        // const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        // ground.rotation.x = -Math.PI / 2;
        // ground.receiveShadow = true;
        // this.scene.add(ground);

        // Grid helper (commented out - not needed with Gaussian Splatting environment)
        // const gridHelper = new THREE.GridHelper(20, 40, 0x0f3460, 0x0f3460);
        // gridHelper.material.opacity = 0.3;
        // gridHelper.material.transparent = true;
        // this.scene.add(gridHelper);
    }

    async loadRobotModel() {
        console.log('[Renderer] Loading GO2 robot OBJ meshes...');

        this.robotGroup = new THREE.Group();
        this.scene.add(this.robotGroup);

        const materials = {
            metal: new THREE.MeshStandardMaterial({ color: 0xe8f0f0, metalness: 0.6, roughness: 0.4 }),
            black: new THREE.MeshStandardMaterial({ color: 0x000000, metalness: 0.3, roughness: 0.7 }),
            white: new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.2, roughness: 0.5 }),
            gray: new THREE.MeshStandardMaterial({ color: 0xabc0c6, metalness: 0.4, roughness: 0.6 })
        };

        // Load base meshes
        const baseGroup = new THREE.Group();
        baseGroup.name = 'base_link';
        this.robotGroup.add(baseGroup);
        this.bodyMeshes['base_link'] = baseGroup;

        const baseMeshes = ['base_0', 'base_1', 'base_2', 'base_3', 'base_4'];
        for (let i = 0; i < baseMeshes.length; i++) {
            const mat = i === 3 ? materials.white : (i === 4 ? materials.gray : materials.black);
            await this.loadObjToGroup(baseMeshes[i], baseGroup, mat);
        }

        // Load leg meshes
        const legConfigs = [
            { name: 'FL', pos: [0.1934, 0.0465, 0], hipY: 0.0955, thighMesh: 'thigh', calfMesh: 'calf' },
            { name: 'FR', pos: [0.1934, -0.0465, 0], hipY: -0.0955, thighMesh: 'thigh_mirror', calfMesh: 'calf_mirror' },
            { name: 'RL', pos: [-0.1934, 0.0465, 0], hipY: 0.0955, thighMesh: 'thigh', calfMesh: 'calf' },
            { name: 'RR', pos: [-0.1934, -0.0465, 0], hipY: -0.0955, thighMesh: 'thigh_mirror', calfMesh: 'calf_mirror' }
        ];

        for (const cfg of legConfigs) {
            // Hip group
            const hipGroup = new THREE.Group();
            hipGroup.name = `${cfg.name}_hip`;
            hipGroup.position.set(...cfg.pos);
            baseGroup.add(hipGroup);
            this.bodyMeshes[`${cfg.name}_hip`] = hipGroup;

            await this.loadObjToGroup('hip_0', hipGroup, materials.metal);
            await this.loadObjToGroup('hip_1', hipGroup, materials.gray);

            // Thigh group
            const thighGroup = new THREE.Group();
            thighGroup.name = `${cfg.name}_thigh`;
            thighGroup.position.set(0, cfg.hipY, 0);
            hipGroup.add(thighGroup);
            this.bodyMeshes[`${cfg.name}_thigh`] = thighGroup;

            await this.loadObjToGroup(`${cfg.thighMesh}_0`, thighGroup, materials.metal);
            await this.loadObjToGroup(`${cfg.thighMesh}_1`, thighGroup, materials.gray);

            // Calf group
            const calfGroup = new THREE.Group();
            calfGroup.name = `${cfg.name}_calf`;
            calfGroup.position.set(0, 0, -0.213);
            thighGroup.add(calfGroup);
            this.bodyMeshes[`${cfg.name}_calf`] = calfGroup;

            await this.loadObjToGroup(`${cfg.calfMesh}_0`, calfGroup, materials.gray);
            await this.loadObjToGroup(`${cfg.calfMesh}_1`, calfGroup, materials.black);
            await this.loadObjToGroup('foot', calfGroup, materials.black);
        }

        this.robotGroup.visible = false;
        this.isLoading = false;
        console.log(`[Renderer] Loaded ${this.loadedMeshCount} meshes`);
    }

    async loadObjToGroup(meshName, group, material) {
        return new Promise((resolve) => {
            const path = `/assets/${meshName}.obj`;

            this.objLoader.load(
                path,
                (obj) => {
                    obj.traverse((child) => {
                        if (child.isMesh) {
                            child.material = material;
                            child.castShadow = true;
                            child.receiveShadow = true;
                        }
                    });
                    group.add(obj);
                    this.loadedMeshCount++;
                    resolve();
                },
                undefined,
                (error) => {
                    console.warn(`[Renderer] Failed to load ${meshName}:`, error);
                    this.loadedMeshCount++;
                    resolve();
                }
            );
        });
    }

    updateRobotState(state) {
        if (this.isLoading || !state) return;

        const shouldShowRobot = !this.robotGroup.visible;

        // Update base position and orientation
        if (state.base_pos && state.base_quat && this.bodyMeshes['base_link']) {
            const pos = state.base_pos;
            const quat = state.base_quat;

            // Convert MuJoCo (Z-up) to Three.js (Y-up): (x,y,z) -> (x,z,-y)
            this.bodyMeshes['base_link'].position.set(pos[0], pos[2], -pos[1]);

            // Convert quaternion with coordinate system rotation
            // MuJoCo quat: [w,x,y,z] in Z-up
            // Create rotation to convert Z-up to Y-up (-90° around X)
            const coordRotation = new THREE.Quaternion();
            coordRotation.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);

            // MuJoCo quaternion in Three.js format
            const mujocoQuat = new THREE.Quaternion(quat[1], quat[2], quat[3], quat[0]);

            // Apply coordinate system rotation
            const finalQuat = coordRotation.multiply(mujocoQuat);
            this.bodyMeshes['base_link'].quaternion.copy(finalQuat);
        }

        // Update joint angles
        if (state.joint_pos) {
            const joints = state.joint_pos;
            const legs = ['FL', 'FR', 'RL', 'RR'];

            legs.forEach((leg, legIdx) => {
                const offset = legIdx * 3;
                if (this.bodyMeshes[`${leg}_hip`]) {
                    this.bodyMeshes[`${leg}_hip`].rotation.x = joints[offset];
                }
                if (this.bodyMeshes[`${leg}_thigh`]) {
                    this.bodyMeshes[`${leg}_thigh`].rotation.y = joints[offset + 1];
                }
                if (this.bodyMeshes[`${leg}_calf`]) {
                    this.bodyMeshes[`${leg}_calf`].rotation.y = joints[offset + 2];
                }
            });
        }

        if (shouldShowRobot) {
            this.robotGroup.visible = true;
            console.log('[Renderer] Robot visible');
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);

        if (window.uiController) {
            window.uiController.incrementFrameCount();
        }
    }

    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    async loadSplatScene(spzPath) {
        console.log('[Renderer] Loading Gaussian Splatting environment scene:', spzPath);

        try {
            // Create SplatMesh instance
            const splatMesh = new SplatMesh({ url: spzPath });

            // Set position and rotation
            // Adjust Y coordinate (height) to align with robot: 0 = ground level, negative = lower, positive = higher
            let splatPosY = 0.6;
            splatMesh.position.set(0, splatPosY, 0);  // X, Y(height), Z
            splatMesh.quaternion.set(1, 0, 0, 0);  // Identity rotation

            // Set scale (adjust to enlarge/shrink the scene)
            // 1.0 = original size, 2.0 = double size, 0.5 = half size
            let sceneScale = 1;
            splatMesh.scale.set(sceneScale, sceneScale, sceneScale);  // X, Y, Z scale

            // Add to scene
            this.scene.add(splatMesh);

            console.log('[Renderer] Gaussian Splatting environment scene loaded successfully');
            return splatMesh;

        } catch (error) {
            console.error('[Renderer] Error loading Gaussian Splat scene:', error);
            throw error;  // Let main.js handle the error
        }
    }

    dispose() {
        console.log('[Renderer] Disposing resources...');

        // Dispose splat scene (if loaded)
        // Note: SplatMesh is stored in scene, traverse to find and dispose
        this.scene.traverse((child) => {
            if (child.constructor.name === 'SplatMesh') {
                this.scene.remove(child);
                if (child.dispose) {
                    child.dispose();
                }
            }
        });

        // Dispose robot meshes
        for (const [name, group] of Object.entries(this.bodyMeshes)) {
            group.traverse((child) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) child.material.dispose();
            });
            this.robotGroup.remove(group);
        }
        this.bodyMeshes = {};
        if (this.controls) this.controls.dispose();
    }
}

export default RobotRenderer;
window.RobotRenderer = RobotRenderer;
