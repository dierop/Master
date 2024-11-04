// ejemplo loader

var loader;
var renderer, scene, camera;
var cameraControls;
var angulo = -0.01;

const clock = new THREE.Clock();

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
  camera = new THREE.PerspectiveCamera( 50, aspectRatio , 1, 1000 );
  camera.position.set( 100, 150, 200 );

  cameraControls = new THREE.OrbitControls( camera, renderer.domElement );
  cameraControls.target.set( 0, 0, 0 );

  const light = new THREE.PointLight(0xffffff, 1, 100);
  light.position.set(50, 50, 50);
  scene.add(light);
  
  // O también una luz ambiental para afectar a todos los objetos de manera uniforme
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);
  

  window.addEventListener('resize', updateAspectRatio );
}

function loadScene()
{
  let material = new THREE.MeshBasicMaterial({color: 0x00ff00});
  let geometryPiso = new THREE.PlaneGeometry(1000, 1000, 100, 100);
  let suelo = new THREE.Mesh(geometryPiso,material);
  suelo.rotateOnAxis(new THREE.Vector3(1, 0, 0), -Math.PI/2) ;

  let geometryBase = new THREE.CylinderGeometry( 50, 50, 15, 32 ); 
  let materialBase = new THREE.MeshBasicMaterial({color: 0x999999, side: THREE.DoubleSide});
  let base = new THREE.Mesh( geometryBase, materialBase );
  base.position.set(0, 7,5, 0);

  let brazo = new THREE.Object3D();
  brazo.position.set(0, 18, 0);

  let geometryEje = new THREE.CylinderGeometry( 20, 20, 18, 32 );
  let materialEje = new THREE.MeshBasicMaterial({color: 0xE82121});
  let eje = new THREE.Mesh( geometryEje, materialEje );
  eje.rotateOnAxis(new THREE.Vector3(1, 0, 0), Math.PI/2) ;
  
  brazo.add(eje);

  let geometryEsparrago = new THREE.BoxGeometry( 18, 120, 12, 32,32 );
  let materialEsparrago = new THREE.MeshBasicMaterial({color: 0x3C21E8});
  let esparrago = new THREE.Mesh( geometryEsparrago, materialEsparrago );
  esparrago.position.set(0, 60, 0);
  brazo.add(esparrago);

  let geometryRotula = new THREE.SphereGeometry( 20, 32, 32 );
  let materialRotula = new THREE.MeshBasicMaterial({color: 0xE82198});
  let rotula = new THREE.Mesh( geometryRotula, materialRotula );
  rotula.position.set(0, 120, 0);
  brazo.add(rotula);

  let antebrazo = new THREE.Object3D();
  antebrazo.position.set(0, 120, 0);
  brazo.add(antebrazo);

  let geometryDisco = new THREE.CylinderGeometry( 22, 22, 6, 32 );
  let materialDisco = new THREE.MeshBasicMaterial({color: 0x21E8E8});
  let disco = new THREE.Mesh( geometryDisco, materialDisco );
  antebrazo.add(disco);

  nervios = [];
  let geometryNervio = new THREE.BoxGeometry(4,80,4,32,32);
  let materialNervio = new THREE.MeshBasicMaterial({color: 0xF6F613});
  
  for (let i = 0; i < 4; i++) {
    nervios[i] = new THREE.Mesh( geometryNervio, materialNervio );
    angulo = (2 * Math.PI / 4) * i
    nervios[i].position.set(Math.cos(angulo)*11, 40, Math.sin(angulo)*11);
    antebrazo.add(nervios[i]);
  }
  let mano = new THREE.Object3D();
  let geometryMano = new THREE.CylinderGeometry( 15, 15, 40, 32 );
  let materialMano = new THREE.MeshBasicMaterial({color: 0x21E8E8});
  let manobase = new THREE.Mesh( geometryMano, materialMano );
  manobase.rotateOnAxis(new THREE.Vector3(1, 0, 0), Math.PI/2) ;
  mano.add(manobase);
  mano.position.set(0, 80, 0);

  var materialDedo = new THREE.MeshBasicMaterial({
    color: 0x444427,   // Black
    // 
    transparent: true
  });
  let geometryDedoPiramide = new THREE.BufferGeometry();
  // Define los vértices 
  var vertices = new Float32Array([
    // Cara 1
    0,  0,  0,  
    19,  5,  0,    
    19,  15, 0,   
    // Cara 1 segundo triangulo
    0,  0,  0,  
    19,  15, 0,  
    0,  20, 0,    
    // Cara 2
    19,  5,  0,
    19,  15, -2, 
    19,  15, 0, 
    // Cara 2 segundo triangulo
    19,  5,  0,
    19,  5, -2, 
    19,  15, -2, 
    // Cara 3
    19,  5, -2,
    0,  0,  -4,
    19,  15, -2, 
    // Cara 3 segundo triangulo
    0,  0,  -4,
    0,  20,  -4,
    19,  15, -2,
    // Cara 4
    0,  0,  -4,
    0,  20,  0,
    0,  20,  -4,
    // Cara 4 segundo triangulo
    0,  0,  -4,
    0,  0,  0,
    0,  20,  0,
    // Base abajo
    0,  0,  0,
    19,  5, -2,
    19,  5,  0,
    // Base abajo segundo triangulo
    0,  0,  0,
    0,  0,  -4,
    19,  5, -2,
    // Base arriba
    0,  20,  0,
    19,  15, 0,
    19,  15, -2,
    // Base arriba segundo triangulo
    0,  20,  0,
    19,  15, -2,
    0,  20,  -4,
  ]);


  geometryDedoPiramide.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
  let dedoPiramide = new THREE.Mesh(geometryDedoPiramide, materialDedo);
  // Crear el material de la malla que soporta colores por vértice
  
  let geometrydedoCubo = new THREE.BoxGeometry( 19, 20, 4, 32,32 );
  let dedoCubo = new THREE.Mesh( geometrydedoCubo, materialDedo );
  dedoCubo.position.set(-9.5, 10, -2);
  

  let dedoD = new THREE.Object3D();
  dedoD.add(dedoCubo);
  dedoD.add(dedoPiramide);
  dedoD.position.set(19, -10, -10);


  dedoI = dedoD.clone();
  dedoI.rotateOnAxis(new THREE.Vector3(1, 0, 0), Math.PI);
  dedoI.position.set(19, 10, 10);
  scene.add(dedoI);
  scene.add(dedoD);

  mano.add(dedoD);
  mano.add(dedoI);

  antebrazo.add(mano);

  

  scene.add( base );
  scene.add(suelo);

  scene.add(brazo);

}

function updateAspectRatio()
{
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}

function update()
{
    // Cambios para actualizar la camara segun mvto del raton
    cameraControls.update();

}

function render()
{
	requestAnimationFrame( render );
	update();
	renderer.render( scene, camera );
}
