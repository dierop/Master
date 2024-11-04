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
  escalera_plano = new THREE.Object3D();

  // Crear escalera
  for (var i = 0; i < 10; i++) {
    var geometry = new THREE.BoxGeometry(10, 1, 1);
    var material = new THREE.MeshBasicMaterial({color: 0x00ff00});
    var cube = new THREE.Mesh(geometry, material);
    cube.position.set(0, i, i);
    escalera_plano.add(cube);
  }
  // const geometry = new THREE.BoxGeometry( 10, 1, 1 ); 
  // const material = new THREE.MeshBasicMaterial( {color: 0x00ff00} ); 
  // const cube = new THREE.Mesh( geometry, material ); 
  scene.add( escalera_plano );

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
