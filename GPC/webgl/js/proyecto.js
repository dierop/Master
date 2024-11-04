var renderer, scene, camera;

var cameraTop;

// Raycaster para interacciones
const raycaster = new THREE.Raycaster();
var objectsToCheck;
const interactionDistance = 5;
const stats = new Stats();
var spotLight;
// Variable para mantener un registro de la habitación que está rotando actualmente
let currentRoom = null;
let targetRotationY = 0;
let isRotating = false;
let rotationSpeed = 0.01;
// Variables para las puertas izquierda y derecha
const ldoors = [];
const rdoors = [];
// Variables para las habitaciones que rotan
const turningRooms = [];
const clock = new THREE.Clock();

// Variables del jugador
var player_obj;
var angulo = -0.01;
var p_pos = new THREE.Vector3(-42.5,1.5,-42.5);
const controls = {
    moveForward: false,
    moveBackward: false,
    moveLeft: false,
    moveRight: false,
    speed: 0.25,
    interaccion: false
};
const end_pos = new THREE.Vector3(41.5,0.1,43);

// Event listeners para controles
document.addEventListener('keydown', (event) => {
  switch (event.code) {
      case 'ArrowUp':
      case 'KeyW':
          controls.moveForward = true;
          break;
      case 'ArrowDown':
      case 'KeyS':
          controls.moveBackward = true;
          break;
      case 'ArrowLeft':
      case 'KeyA':
          controls.moveLeft = true;
          break;
      case 'ArrowRight':
      case 'KeyD':
          controls.moveRight = true;
          break;
      case 'KeyF':
          controls.interaccion = true;
          break;
  }
});

document.addEventListener('keyup', (event) => {
switch (event.code) {
    case 'ArrowUp':
    case 'KeyW':
        controls.moveForward = false;
        break;
    case 'ArrowDown':
    case 'KeyS':
        controls.moveBackward = false;
        break;
    case 'ArrowLeft':
    case 'KeyA':
        controls.moveLeft = false;
        break;
    case 'ArrowRight':
    case 'KeyD':
        controls.moveRight = false;
        break;
    case 'KeyF':
        controls.interaccion = false;
        break;
}
});
// Pared base
const txPared = new THREE.TextureLoader().load("textura/pared.jpg");
const wall = new THREE.Mesh(new THREE.BoxGeometry(5, 5, 1, 100), new THREE.MeshLambertMaterial({map: txPared, shading: THREE.SmoothShading}));
wall.castShadow = true;
wall.receiveShadow = true;

init();
render();

function creaPuerta(xpos, ypos, zpos){
  var txPuertaD = new THREE.TextureLoader().load("textura/puerta_derecha.png");
  const eje = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5, 1, 32), new THREE.MeshBasicMaterial({transparent: true, opacity: 0}));
  eje.position.set(xpos-1.25, 2, zpos);
  let puertaD = new THREE.Mesh(new THREE.BoxGeometry(2.5, 4, 0.5, 100), new THREE.MeshPhongMaterial({map: txPuertaD, shininess:2}));
  puertaD.castShadow = true;
  puertaD.position.x = 1.25;
  eje.add(puertaD);
  const ejeI = eje.clone();
  ejeI.rotation.y = Math.PI;
  ejeI.position.x=xpos+3.75;

  var txTopPuerta = new THREE.TextureLoader().load("textura/puerta_top.png");
  let puertaTop = new THREE.Mesh(new THREE.BoxGeometry(2.5,1, 0.5, 100), new THREE.MeshPhongMaterial({map: txTopPuerta}));
  puertaTop.position.set(xpos, 4.5, zpos);
  
  let puertaTopI = puertaTop.clone();
  puertaTopI.rotation.y = Math.PI;
  puertaTopI.position.x = xpos + 2.5;

  let door = new THREE.Object3D();
  door.add(eje);
  door.add(ejeI);
  door.add(puertaTop);
  door.add(puertaTopI);
  rdoors.push(eje);
  ldoors.push(ejeI);
  return door;

}
function create_turning_room(room, x, y, z, rotationY = 0) {
  let txtPilar = new THREE.TextureLoader().load("textura/pilar.png");
  let pilar = new THREE.Mesh(new THREE.BoxGeometry(0.5, 1.5, 0.5, 32), new THREE.MeshPhongMaterial({map: txtPilar,specular:0xFAAFAA, shininess:50}));
  pilar.position.set(0, 0.75, 0);
  let sphere = new THREE.Mesh(new THREE.SphereGeometry(0.25, 32, 32), new THREE.MeshPhongMaterial({color: 0x000000,specular:0xFAAFAA, shininess:50}));
  sphere.position.set(0, 0.75, 0);
  pilar.add(sphere);
  pilar.castShadow = true;
  pilar.receiveShadow = true;
  room.add(pilar);
  room.position.set(x, y, z);
  room.rotation.y = rotationY;
  room.isRotating = false;
  room.targetRotationY = rotationY;
  turningRooms.push(room);
  scene.add(room);
}

function create_sized_wall(x, y, z, quantity, rotationY = 0) {
  sized_wall = new THREE.Object3D();

  for (let i = 0; i < quantity; i++)
  {
    w = wall.clone();
    w.position.set(5*i, 2.5, 2.5+5);
    sized_wall.add(w);
  }
  sized_wall.position.set(x, y, z);
  sized_wall.rotation.y = rotationY;
  scene.add(sized_wall);
}
function createTorch(x, y, z, rotationY = 0) {
  const extra_torch = new THREE.DirectionalLight(0xffa95c, 0.2,5);
  extra_torch.position.set(x, y, z);
  scene.add(extra_torch);
  
  torchLight = new THREE.SpotLight(0xffa95c, 4); // Luz cálida con intensidad 2
  torchLight.angle = Math.PI / 6; // Ángulo del cono de luz
  torchLight.penumbra = 0.3; // Suavidad de los bordes del foco
  torchLight.decay = 3; // Atenuación de la luz con la distancia
  torchLight.distance = 20; // Distancia máxima de la luz
  torchLight.castShadow = true;
  torchLight.position.set(x, y+3, z); 
  torchLight.target.position.set(
      x, 
      y-1,
      z
  );
  torchLight.target.updateMatrixWorld()
  scene.add(torchLight);
  const loader = new THREE.GLTFLoader();
  const model = 'models/antorcha_medieval/scene.gltf';
  loader.load(model, function(gltf) {
    const object = gltf.scene;
    object.scale.set(4,4,4);
    object.position.set(x,y,z);
    object.rotation.y = rotationY;
    object.castShadow = true;
    object.receiveShadow = true;
    scene.add(object);
  });
}

function init()
{
  renderer = new THREE.WebGLRenderer();
  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.setClearColor( new THREE.Color(0x000000) );
  renderer.shadowMap.enabled = true;
  document.getElementById('container').appendChild( renderer.domElement );

  scene = new THREE.Scene();


  loadScene();

  var aspectRatio = window.innerWidth / window.innerHeight;
  near_plane = 1;
  camera = new THREE.PerspectiveCamera( 50, aspectRatio , near_plane, 1000 );
  camera.position.set( 5, 0, 0 );

  cameraControls = new THREE.OrbitControls( camera, renderer.domElement );
  cameraControls.target.set( 0, -1, 0 );

  // Luz puntual en la posición final
  const light = new THREE.PointLight(0x641e1c, 0.6, 100);
  light.position.set(end_pos.x, 2.5, end_pos.z+2);
  scene.add(light);
  // Luz focal del pj
  spotLight = new THREE.SpotLight(0xffa95c, 2); // Luz cálida con intensidad 2
  spotLight.angle = Math.PI / 8; // Ángulo del cono de luz
  spotLight.penumbra = 0.2; // Suavidad de los bordes del foco
  spotLight.decay = 2; // Atenuación de la luz con la distancia
  spotLight.distance = 20; // Distancia máxima de la luz
  spotLight.castShadow = true; // Producir sombras
  scene.add(spotLight);

  
  createTorch(-43,2,-23.5, Math.PI/2); 
  createTorch(46.5,2,-46.5, 6*Math.PI/4); 
  // createTorch(29,2,-36.5, -Math.PI/2 );
  createTorch(-24, 2, -5, Math.PI);
  createTorch(-15, 2, 19, -Math.PI/2);
  createTorch(-46, 2, -0.5);
  createTorch(-46, 2, 47, Math.PI/2);
  createTorch(-1, 2, 41, Math.PI/4);
  createTorch(19, 2, -16.5,);
  createTorch(46, 2, 25, Math.PI/2);
  // luz ambiental 
  const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
  scene.add(ambientLight);
  // luz direccional
  const directionalLight = new THREE.DirectionalLight(0x404040, 0.1); 
    directionalLight.position.set(0, 50, 0);
    scene.add(directionalLight);

  // STATS --> stats.update() en update()
	stats.showPanel(0);	// FPS inicialmente. Picar para cambiar panel.
	document.getElementById( 'container' ).appendChild( stats.domElement );

  // cammara minimapa
  cameraTop = new THREE.OrthographicCamera( -48, 49, 48,-49, 1, 1000 );
  cameraTop.position.set(0,500,0);
  cameraTop.lookAt( 0, 0, 0 );
  cameraTop.up.set( 0, 0, 1 );
  cameraTop.updateProjectionMatrix();  

  window.addEventListener('resize', updateAspectRatio );
}

function loadScene()
{
  // cielo
  let txCielo = new THREE.TextureLoader().load("textura/cielo.jpg");
  txCielo.wrapS = txCielo.wrapT = THREE.MirroredRepeatWrapping;
  txCielo.repeat.set(3,3);
  txCielo.magFilter = THREE.LinearFilter;
  txCielo.minFilter = THREE.LinearFilter;

  let cielo = new THREE.Mesh(new THREE.PlaneGeometry(1000, 1000), new THREE.MeshBasicMaterial({map: txCielo}));
  cielo.rotation.x = Math.PI / 2;
  cielo.position.set(0, 40, 0);
  scene.add(cielo);
  // suelo
  let txSuelo = new THREE.TextureLoader().load("textura/suelo.jpg");
  txSuelo.wrapS =txSuelo.wrapT= THREE.MirroredRepeatWrapping;
  txSuelo.repeat.set(5,5);
  txSuelo.magFilter = THREE.LinearFilter;
  txSuelo.minFilter = THREE.LinearFilter;
  let floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100, 10, 10), new THREE.MeshPhongMaterial({map: txSuelo}));
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, -0.1, 0);
  floor.receiveShadow = true;
  scene.add(floor);


  // paredes
  //horizontales
  create_sized_wall(-50, 0, -30, 9);
  create_sized_wall(-15, 0, -45, 10);
  create_sized_wall(-15, 0, -50, 10);
  create_sized_wall(10, 0, -35, 8);
  create_sized_wall(-30, 0, -20, 8);
  create_sized_wall(-50, 0, -10, 10);
  create_sized_wall(-25, 0, -15, 3);
  create_sized_wall(-40, 0, -25, 1);
  create_sized_wall(-40, 0, -15, 1);
  create_sized_wall(-40, 0, 35, 8);
  create_sized_wall(-40, 0, 20, 6);
  create_sized_wall(-40, 0, 5, 1);
  create_sized_wall(-30, 0, 5, 1);
  create_sized_wall(-20, 0, 10, 2);
  create_sized_wall(-25, 0, 30, 5);
  create_sized_wall(10, 0, 27.5, 6);
  create_sized_wall(0, 0, 20, 6);
  create_sized_wall(0, 0, 35, 5);
  create_sized_wall(15, 0, 5, 1);
  create_sized_wall(25, 0, 5, 1);
  create_sized_wall(30, 0, -5, 3);
  create_sized_wall(40, 0, -15, 2);
  create_sized_wall(40, 0, 10, 1);
  create_sized_wall(40, 0, 20, 2);
  // verticales
  create_sized_wall(0, 0, -5, 5, Math.PI/2);
  create_sized_wall(-35, 0, -30, 4, Math.PI/2);
  create_sized_wall(-30, 0, -25, 4, Math.PI/2);
  create_sized_wall(-15, 0, -25, 3, Math.PI/2);
  create_sized_wall(-5, 0, -15, 3, Math.PI/2);
  create_sized_wall(-25, 0, -30, 2, Math.PI/2);
  create_sized_wall(-30, 0, -5, 1, Math.PI/2);
  create_sized_wall(-40, 0, -10, 1, Math.PI/2);
  create_sized_wall(-15, 0, -10, 1, Math.PI/2);
  create_sized_wall(-45, 0, -10, 2, Math.PI/2);
  create_sized_wall(-50, 0, -10, 2, Math.PI/2);
  create_sized_wall(-10, 0, 40, 7, Math.PI/2);
  create_sized_wall(-50, 0, 40, 8, Math.PI/2);
  create_sized_wall(-35, 0, 25, 3, Math.PI/2);
  create_sized_wall(-25, 0, 15, 4, Math.PI/2);
  create_sized_wall(-20, 0, 20, 2, Math.PI/2);
  create_sized_wall(5, 0, 20, 5, Math.PI/2);
  create_sized_wall(10, 0, 25, 9, Math.PI/2);
  create_sized_wall(25, 0, 32.5, 8, Math.PI/2);
  create_sized_wall(20, 0, 25, 3, Math.PI/2);
  create_sized_wall(15, 0, 0, 1, Math.PI/2);
  create_sized_wall(35, 0, 25, 2, Math.PI/2);
  create_sized_wall(30, 0, 25, 2, Math.PI/2);
  // make End walls
  create_sized_wall(-49, 0, 41, 20);
  create_sized_wall(-50, 0, -55, 20);
  create_sized_wall(-55, 0, 50, 20, Math.PI/2);
  create_sized_wall(41, 0, 50, 20, Math.PI/2);


  // Base room with one opening
  room = new THREE.Object3D();
  max=7.5
  for (let i = -1; i <= 1; i++)
    
  {
    if (i!=0){
      w1 = wall.clone();
      w1.position.set(5*i, 2.5, -max+0.25);
      room.add(w1);
    }
    w2 = wall.clone();
    w2.rotation.y = Math.PI / 2;
    w2.position.set(-max, 2.5, 5*i);
    room.add(w2);

    w3 = wall.clone();
    w3.rotation.y = Math.PI / 2;
    w3.position.set(max, 2.5, 5*i);
    room.add(w3);

    w4 = wall.clone();
    w4.position.set(5*i, 2.5, max);
    room.add(w4);
    
  }
  const roomEnd = room.clone();
  
  // habitación de fin - Verde
  let SueloFin = new THREE.Mesh(new THREE.PlaneGeometry(12.5, 12.5, 10, 10), new THREE.MeshPhongMaterial({color: 0x00ff00}));
  SueloFin.rotation.x = -Math.PI / 2;
  SueloFin.position.set(-1, 0,-1 );
  SueloFin.receiveShadow = true;
  roomEnd.add(SueloFin);
  const enddoor = creaPuerta(41.25, 0, 35);
  scene.add(enddoor);
  roomEnd.position.set(42.5, 0, 42.5);
  scene.add(roomEnd);
  const loader = new THREE.GLTFLoader();
  const model = 'models/cofre/scene.gltf';
  loader.load(model, function(gltf) {
    const object = gltf.scene;
    object.scale.set(0.01, 0.006, 0.01);
    object.position.set(end_pos.x+1,end_pos.y, end_pos.z);
    object.rotation.y = Math.PI;
    object.castShadow = true;
    object.receiveShadow = true;
    scene.add(object);
  });

  // habitación de inicio - Rojo
  const roomStart = room.clone();
  let SueloIni = new THREE.Mesh(new THREE.PlaneGeometry(12.5, 12.5, 10, 10), new THREE.MeshPhongMaterial({color: 0xff0000}));
  SueloIni.rotation.x = -Math.PI / 2;
  SueloIni.position.set(-1, 0,-1 );
  SueloIni.receiveShadow = true;
  roomStart.add(SueloIni);
  const startdoor = creaPuerta(-43.75, 0, -35.5);
  scene.add(startdoor);
  roomStart.rotation.y = Math.PI;
  roomStart.position.set(-42.5, 0, -42.5);
  
  scene.add(roomStart);

  // Tunring room
  create_turning_room(room.clone(), 5, 0, 5);
  create_turning_room(room.clone(), 40, 0, -40 , Math.PI/2);
  create_turning_room(room.clone(), 25, 0, -10 , Math.PI);
  

  player_obj = new THREE.Mesh(new THREE.SphereGeometry(3,1 ,5), 
            new THREE.MeshBasicMaterial( {color: 0xff0000 }));
  scene.add(player_obj);

  objectsToCheck = scene.children.filter(obj => obj !== player_obj); 


}

function updateAspectRatio()
{
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}

var time = 0;
var startTime = Date.now(); 
var timer = 0;
var timerElement = document.getElementById('timer');
var gameActive = true;
function update()
{
    time += 0.01;

    if (gameActive) {
      timer =Math.floor((Date.now() - startTime) / 1000);
      
      timerElement.innerHTML = "Time: " + timer + "s";

    // Actualizar el ángulo basado en los controles de izquierda y derecha
    if (controls.moveLeft) angulo += 0.05;
    if (controls.moveRight) angulo -= 0.05;
    // Calcular el vector de dirección de vista
    let velocity = new THREE.Vector3(Math.sin(angulo), 0, Math.cos(angulo));
    if (controls.moveForward) {
      
      // Configurar el rayo desde la posición actual del jugador y en la dirección de movimiento
      raycaster.set(p_pos, velocity);
      // Detectar intersecciones con objetos en la escena (por ejemplo, las paredes)
      const intersects = raycaster.intersectObjects(objectsToCheck, true);

      // Si no hay intersección, permitir el movimiento
      if (intersects.length === 0 || intersects[0].distance > controls.speed+near_plane+2) {
      // mueve el personaje
          p_pos.add(velocity.clone().multiplyScalar(controls.speed));
      }
      else{
          let bp = 1;
      }
    }  
    // Abrir/Cerrar puertas izquierda
    rdoors.forEach((door) => {
      // door.getWorldPosition(worldPosition); // Obtener la posición mundial de la puerta
        let dist = p_pos.distanceTo(door.position);
      if (dist < 7.5) { // Si está cerca de la puerta
          if (controls.interaccion && door.rotation.y > -Math.PI / 2) {
              door.rotation.y -= 0.01; // Abrir la puerta izquierda hacia la izquierda
          } else if (!controls.interaccion && door.rotation.y < 0) {
              door.rotation.y += 0.01; // Cerrar la puerta izquierda
          }
      }else if (door.rotation.y < 0) {
        door.rotation.y += 0.01; // Cerrar la puerta izquierda
    }
  });

  // Abrir/Cerrar puertas derecha
  ldoors.forEach((door) => {
    // door.getWorldPosition(worldPosition); // Obtener la posición mundial de la puerta
    let dist = p_pos.distanceTo(door.position);
      if (dist < 7.5) { // Si está cerca de la puerta
          if (controls.interaccion && door.rotation.y < Math.PI *3/2) {
              door.rotation.y += 0.01; // Abrir la puerta derecha hacia la derecha
          } else if (!controls.interaccion && door.rotation.y > Math.PI) {
              door.rotation.y -= 0.01; // Cerrar la puerta derecha
          }
      } else if ( door.rotation.y > Math.PI) {
        door.rotation.y -= 0.01; // Cerrar la puerta derecha
    }
  });


  
    if (controls.interaccion && !isRotating){
      let closestRoom = null;
      let minDist = interactionDistance;

        turningRooms.forEach((room) => {
            let dist = p_pos.distanceTo(room.position);
            if (dist < minDist) {
                minDist = dist;
                closestRoom = room; // Habitación más cercana dentro del rango
            }
        });
        if (closestRoom) {
          currentRoom = closestRoom; // Guardamos la habitación que vamos a rotar
          closestRoom.targetRotationY += Math.PI / 2; // Sumar 90 grados
          isRotating = true; // Activamos la bandera de rotación
      }
    };
    if (isRotating && currentRoom) {
      // Interpolar la rotación hacia el objetivo
      if (Math.abs(currentRoom.rotation.y - currentRoom.targetRotationY) > rotationSpeed) {
          currentRoom.rotation.y += rotationSpeed * Math.sign(currentRoom.targetRotationY - currentRoom.rotation.y);
      } else {
          // Detener la rotación cuando alcanzamos el objetivo
          currentRoom.rotation.y = currentRoom.targetRotationY; // Ajustar la rotación exacta
          isRotating = false; // Desactivar la rotación
      }
  };
  
  
    // actualizo la pos. del mesh que representa el jugador
    player_obj.position.set(p_pos.x, p_pos.y, p_pos.z);
    player_obj.rotation.y = angulo + Math.PI/2;


    // camara en primera persona
    camera.position.set(p_pos.x, p_pos.y, p_pos.z);
    // y mirando hacia adelante
    camera.lookAt(new THREE.Vector3().addVectors(p_pos, velocity.multiplyScalar(25)));
  
    spotLight.position.set(p_pos.x, p_pos.y, p_pos.z-1);
    spotLight.target.position.set(
      p_pos.x + velocity.x * 10, // Apuntar hacia adelante en la dirección del movimiento
      p_pos.y,
      p_pos.z + velocity.z * 10
  );
  spotLight.target.updateMatrixWorld()
    if (p_pos.distanceTo(end_pos) < interactionDistance) {
      gameActive = false;
      alert("Has ganado en " + timer + " segundos");
  }
    }
    stats.update();
}

function render()
{
  requestAnimationFrame( render );
	update();
  


    // vista 3d perspectiva
    renderer.autoClear = false;
    renderer.setViewport(0,0,window.innerWidth,window.innerHeight);
	renderer.setClearColor( new THREE.Color(0x000000) );
	renderer.clear();
	renderer.render( scene, camera );

    // vista de arriba
    var ds = Math.min(window.innerHeight , window.innerWidth)/4;
    renderer.setViewport(0,0,ds,ds);
	renderer.setScissor (0, 0, ds, ds);
	renderer.setScissorTest (true);
	renderer.setClearColor( new THREE.Color(0xaffff) );
	renderer.clear();	
	renderer.setScissorTest (false);
    renderer.render(scene, cameraTop);

}
