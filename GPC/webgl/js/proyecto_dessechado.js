var renderer, scene, camera;
var angulo = -0.01;
var cameraTop;

const reloj = new THREE.Clock();


var angulo = -0.01;
var p_pos = new THREE.Vector3(-42.5,1.5,-42.5);
const clock = new THREE.Clock();
const loader = new THREE.GLTFLoader();
const controls = {
    moveForward: false,
    moveBackward: false,
    moveLeft: false,
    moveRight: false,
    speed: 50,
    back_speed: -0.1,
    interaccion: false
};

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
          interaccion = true;
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
        interaccion = false;
        break;
}
});
let world;
const groundMaterial = new CANNON.Material("groundMaterial");
const sphereMaterial = new CANNON.Material("sphereMaterial");
const wallMaterial = new THREE.MeshPhongMaterial({ color: 0x888888 }); // Color gris para las paredes
const cannonWallMaterial = new CANNON.Material(); // Material de Cannon.js para físicas
// Parámetros comunes para las paredes
const wallThickness = 1;
const wallHeight = 5;
const wallLength = 5; // Asume que la longitud es la misma que la del suelo
let ShpereBody

// Función para crear una pared
function createWall(x, y, z, rotationY) {

  // Visual
  const wallGeometry = new THREE.BoxGeometry(wallLength, wallHeight, wallThickness);
  const wallMesh = new THREE.Mesh(wallGeometry, wallMaterial);
  wallMesh.position.set(x, y, z);
  wallMesh.rotation.y = rotationY;
  wallMesh.castShadow = true;
  wallMesh.receiveShadow = true;
  scene.add(wallMesh);

  // Físico
  const wallShape = new CANNON.Box(new CANNON.Vec3(wallLength / 2, wallHeight / 2, wallThickness / 2));
  const wallBody = new CANNON.Body({ mass: 0, material: cannonWallMaterial });
  wallBody.addShape(wallShape);
  wallBody.position.set(x, y, z);
  wallBody.quaternion.setFromAxisAngle(new CANNON.Vec3(0, 1, 0), rotationY);
  world.addBody(wallBody);

  // Relación entre físico y visual
  wallMesh.body = wallBody;

  return wallMesh;
}


init();
render();


function init()
{
  renderer = new THREE.WebGLRenderer();
  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.setClearColor( new THREE.Color(0xFFFFFF) );
  document.getElementById('container').appendChild( renderer.domElement );

  scene = new THREE.Scene();


  loadScene();

  var aspectRatio = window.innerWidth / window.innerHeight;
  near_plane = 1;
  camera = new THREE.PerspectiveCamera( 50, aspectRatio , near_plane, 1000 );
  camera.position.set( 5, 0, 0 );

  cameraControls = new THREE.OrbitControls( camera, renderer.domElement );
  cameraControls.target.set( 0, -1, 0 );

  const light = new THREE.PointLight(0xffffff, 1, 100);
  light.position.set(50, 50, 50);
  scene.add(light);
  
  // O también una luz ambiental para afectar a todos los objetos de manera uniforme
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);
  reloj.start();
  
  // vista de planta
  cameraTop = new THREE.OrthographicCamera( -50, 50, 50,-50, 1, 1000 );
  cameraTop.position.set(0,500,0);
  cameraTop.lookAt( 0, 0, 0 );
  cameraTop.up.set( 0, 0, 1 );
  cameraTop.updateProjectionMatrix();  

  window.addEventListener('resize', updateAspectRatio );
}

function loadScene()
{
  // Crear el mundo
  world = new CANNON.World();
  world.gravity.set(0, -20, 0);


  // Suelo
    // visual
  let txSuelo = new THREE.TextureLoader().load("textura/suelo.jpg");
  suelo_material = new THREE.MeshPhongMaterial({map: txSuelo});
	const suelo = new THREE.Mesh( new THREE.PlaneGeometry(5,5,1,1), suelo_material);
	suelo.rotation.x = -Math.PI/2;
	suelo.position.y = -0.25;
  suelo.receiveShadow = true
	scene.add( suelo);
    // fisico
    // en cannon un plane es un plano infinito
  const groundShape = new CANNON.Plane();
  const ground = new CANNON.Body({ mass: 0, material: groundMaterial });
    ground.addShape(groundShape);
	ground.position.y = -0.25;
    ground.quaternion.setFromAxisAngle(new CANNON.Vec3(1,0,0),-Math.PI/2);
    world.addBody(ground);
    // relacion entre fisico y visual
    suelo.body = ground;

  for (let i = -10; i <= 10; i++)
  {
    for (let j =-10; j <= 10; j++)
    {
      suelo1= suelo.clone();
      suelo1.position.set(i*5, 0, j*5);
      scene.add(suelo1);
    }
  }

  var txPared = new THREE.TextureLoader().load("textura/pared.jpg");
  wall = new THREE.Mesh(new THREE.BoxGeometry(5, 5, 1, 100), new THREE.MeshPhongMaterial({map: txPared}));
  wall.position.y = 2.5;

  big_wall = new THREE.Object3D();

  for (let i = 0; i < 10; i++)
  {
    w1 = wall.clone();
    //  Girar la pared
    // w1.rotation.y = Math.PI / 2;
    w1.position.set(5*i, 2.5, 2.5+5);
    big_wall.add(w1);
  }

  // roomEnd
  roomEnd = new THREE.Object3D();
  max=7.5
  // make square roomEnd
  for (let i = -1; i <= 1; i++)
    
  {
    // w1 = wall.clone();
    // w1.position.set(5*i, 2.5, -max);
    // roomEnd.add(w1);

    w2 = wall.clone();
    w2.rotation.y = Math.PI / 2;
    w2.position.set(-max, 2.5, 5*i);
    roomEnd.add(w2);

    w3 = wall.clone();
    w3.rotation.y = Math.PI / 2;
    w3.position.set(max, 2.5, 5*i);
    roomEnd.add(w3);

    w4 = wall.clone();
    w4.position.set(5*i, 2.5, max);
    roomEnd.add(w4);
    
  }
  roomEnd.position.set(42.5, 0, 42.5);
  scene.add(roomEnd);

  roomStart = roomEnd.clone();
  roomStart.rotation.y = Math.PI;
  roomStart.position.set(-42.5, 0, -42.5);
  
  scene.add(roomStart);

  var txPared = new THREE.TextureLoader().load("textura/pared.jpg");
  pared_material = new THREE.MeshPhongMaterial({map: txPared});
  endwall = new THREE.Mesh(new THREE.BoxGeometry(5, 5, 5, 100), pared_material);

  end = new THREE.Object3D();
  // make End walls
  for (let i = -10; i <= 10; i++)
  {
    createWall(wallLength*i, wallHeight / 2, -wallLength*10 + wallThickness/2, 0); // Pared fondo
    createWall(wallLength*i, wallHeight / 2, wallLength *10 - wallThickness / 2, 0); // Pared frente
    createWall(-wallLength*10 + wallThickness/2, wallHeight / 2, wallLength*i, Math.PI / 2); // Pared izquierda
    createWall(wallLength*10 - wallThickness/2, wallHeight / 2, wallLength*i, Math.PI / 2); // Pared derecha
    
  }
  scene.add(end);

  

 player_mat= new THREE.MeshPhongMaterial({color: 0xff0000});
  player_obj = new THREE.Mesh(new THREE.SphereGeometry(3,1 ,5),player_mat);
  player_obj.position.copy(p_pos);
  scene.add(player_obj);


    // Crear el body para Cannon.js
    const ShpereShape = new CANNON.Sphere(3); // La mitad de las dimensiones del Shpere
    ShpereBody = new CANNON.Body({type: CANNON.Body.KINEMATIC, mass: 10 ,material:player_mat}); // Una masa no nula para que pueda moverse
    ShpereBody.addShape(ShpereShape);
    ShpereBody.position.copy(p_pos);
    world.addBody(ShpereBody);

    // // Relacionar el body con el mesh
    player_obj.body = ShpereBody;

  // Material de contacto entre esferas (para Cannon.js)
  const PlayerContactMaterial = new CANNON.ContactMaterial(
    player_mat,
    player_mat, // Utilizar el mismo material por simplicidad
    {
        friction: 0.2,
        restitution: 0.1 // Reducir la restitución para evitar rebotes
    }
);
  world.addContactMaterial(PlayerContactMaterial);

  // Crear un `ContactMaterial` para definir la interacción entre la esfera y el suelo
  const paredContactMaterial = new CANNON.ContactMaterial(
    pared_material,
    pared_material,
      {
          friction: 0.4,         // Coeficiente de fricción
          restitution: 0.1       // Reducir la restitución para evitar rebotes
      }
  );
  world.addContactMaterial(paredContactMaterial); 


  // Crear un `ContactMaterial` para definir la interacción entre la esfera y el suelo
  const sueloContactMaterial = new CANNON.ContactMaterial(
    suelo_material,
    suelo_material,
      {
          friction: 0.8,         // Coeficiente de fricción
          restitution: 0.1       // Reducir la restitución para evitar rebotes

      }
  );
  world.addContactMaterial(sueloContactMaterial); 

  // Obtener una lista de los objetos que no incluyen al jugador
  // objectsToCheck = scene.children.filter(obj => obj !== player_obj); 
  world.allowSleep = true; // Permite que los cuerpos entren en estado de sueño
  // Configurar los parámetros de sueño para todos los cuerpos
  world.bodies.forEach(body => {
  body.sleepSpeedLimit = 0.1; // Velocidad bajo la cual el cuerpo puede dormirse
  body.sleepTimeLimit = 1; // Tiempo en segundos después del cual el cuerpo se dormirá si está por debajo del límite de velocidad
  });

}

function updateAspectRatio()
{
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}

var time = 0;
function update()
{
    time += 0.01;

    // Calcular el vector de dirección de vista
    let velocity = new THREE.Vector3(Math.sin(angulo), 0, Math.cos(angulo));

    // Actualizar el ángulo basado en los controles de izquierda y derecha
    if (controls.moveLeft) angulo += 0.05;
    if (controls.moveRight) angulo -= 0.05;

    // ShpereBody.rotationY = angulo;
    // if (controls.moveForward) {
    //   ShpereBody.velocity.add(velocity.clone().multiplyScalar(controls.speed));
      // Configurar el rayo desde la posición actual del jugador y en la dirección de movimiento
      // raycaster.set(p_pos, velocity);
      // // Detectar intersecciones con objetos en la escena (por ejemplo, las paredes)
      // const intersects = raycaster.intersectObjects(objectsToCheck, true);

      // // Si no hay intersección, permitir el movimiento
      // if (intersects.length === 0 || intersects[0].distance > controls.speed+near_plane+2) {
      // // mueve el personaje
      //     p_pos.add(velocity.clone().multiplyScalar(controls.speed));
      // }
      // else{
      //     let bp = 1;
      // }
    // }  
  
    // actualizo la pos. del mesh que representa el jugador
    // player_obj.position.set(p_pos.x, p_pos.y, p_pos.z);
    // player_obj.rotation.y = angulo + Math.PI/2;


    // camara en primera persona
    camera.position.copy(ShpereBody.position);

    const segundos = reloj.getDelta();	// tiempo en segundos que ha pasado por si hace falte
	  //world.fixedStep()					// recalcula el mundo a periodo fijo (60Hz)
    world.step(segundos);

    // Sincronizar el mesh visual con el cuerpo físico
    // Recorre todos los objetos en la escena
    scene.traverse(function(obj) {
        // Verifica si el objeto tiene una propiedad `body` (CANNON.Body)
        if (obj.body !== undefined) {
            // Sincroniza la posición y rotación del objeto visual con el cuerpo físico
            obj.position.copy(obj.body.position);
            obj.quaternion.copy(obj.body.quaternion);
        }
    });
    // y mirando hacia adelante
    camera.lookAt(new THREE.Vector3().addVectors(p_pos, velocity.multiplyScalar(25)));
  
}
function updatePosition(deltaX, deltaY, deltaZ) {
  ShpereBody.velocity.x += deltaX;
  ShpereBody.velocity.y += deltaY;
  ShpereBody.velocity.z += deltaZ;
}

document.addEventListener('keydown', (event) => {
  switch (event.key) {
      case 'ArrowUp':
          updatePosition(0, 0, -1); // Mover hacia adelante
          break;
      case 'ArrowDown':
          updatePosition(0, 0, 1); // Mover hacia atrás
          break;
      case 'ArrowLeft':
          updatePosition(-1, 0, 0); // Mover hacia la izquierda
          break;
      case 'ArrowRight':
          updatePosition(1, 0, 0); // Mover hacia la derecha
          break;
  }
});


function render()
{
  requestAnimationFrame( render );
	update();

    // vista 3d perspectiva
    renderer.autoClear = false;
    renderer.setViewport(0,0,window.innerWidth,window.innerHeight);
	renderer.setClearColor( new THREE.Color(0xa2a2f2) );
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
