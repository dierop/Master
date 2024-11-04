var camera, scene, renderer;
var mesh, pivot;

init();
animate();

function init() {

    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.01, 10 );
    camera.position.z = 1;

    scene = new THREE.Scene();

    var material = new THREE.MeshNormalMaterial();
    material.side = THREE.DoubleSide;

    axis = new THREE.Mesh( new THREE.PlaneGeometry( 0.01, 0.6, 0.01 ), material );
    axis.position.set(0.4, 0, .20);
    scene.add( axis );

    var door = new THREE.Mesh( new THREE.PlaneGeometry( 0.2, 0.5, 0.2 ), material );
    door.position.set( 0, 0, 0 );
    axis.add(door);

    pivot = new THREE.Group();
    pivot.position.set( 0.0, 0.0, 0 );
    axis.add( pivot );
    pivot.add( door );

    scene.add( new THREE.AxesHelper() );

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );

}

function animate() {

    requestAnimationFrame( animate );

        pivot.rotation.y += 0.01;

    renderer.render( scene, camera );

}