

// Variables globales que van siempre
var renderer, scene, camera;
var cameraControls;
var angulo = -0.01;

// 1-inicializa 
init();
// 2-Crea una escena
loadScene();
// 3-renderiza
render();

function init()
{
  renderer = new THREE.WebGLRenderer();
  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.setClearColor( new THREE.Color(0xFFFFFF) );
  document.getElementById('container').appendChild( renderer.domElement );

  scene = new THREE.Scene();

  var aspectRatio = window.innerWidth / window.innerHeight;
  camera = new THREE.PerspectiveCamera( 50, aspectRatio , 0.1, 100 );
  camera.position.set( 5, 10, 20 );

  cameraControls = new THREE.OrbitControls( camera, renderer.domElement );
  cameraControls.target.set( 0, 0, 0 );

  window.addEventListener('resize', updateAspectRatio );
}


function loadScene() {
    caja1 = new THREE.Mesh(new THREE.BoxGeometry(5,1,3), new THREE.MeshNormalMaterial());
    scene.add(caja1);

    caja2 = new THREE.Mesh(new THREE.BoxGeometry(1,5,3), new THREE.MeshNormalMaterial());
    caja2.position.y = 3;
    caja2.position.x = 3;
    caja1.add(caja2);

    caja3 = new THREE.Mesh(new THREE.BoxGeometry(5,1,3), new THREE.MeshNormalMaterial());
    caja3.position.y = 3;
    caja3.position.x = 3;
    caja2.add(caja3);



    scene.add( new THREE.AxesHelper(15 ) );

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
  // Cambios para actualizar la camara segun mvto del raton
  cameraControls.update();
  //caja1.rotation.z = time;
  let Rz = new THREE.Matrix4();
  Rz.makeRotationZ(time);  
  let Tx = new THREE.Matrix4();
  Tx.makeTranslation(2.5,0,0);
  let Tx1 = new THREE.Matrix4();
  Tx1.makeTranslation(-2.5,0,0);
    // let Ry = new THREE.Matrix4();
    // Ry.makeRotationY(time);  
    // Combinar todas las transformaciones
  let M = new THREE.Matrix4();
  M.multiply(Tx1);
  M.multiply(Rz);
  M.multiply(Tx);
  caja2.matrix.identity();  // Limpiar la matriz actual
  caja2.applyMatrix4(M);    // Aplicar la matriz de transformación combinada
  caja2.matrixAutoUpdate = false
  
}

function render()
{
	requestAnimationFrame( render );
	update();
	renderer.render( scene, camera );
}