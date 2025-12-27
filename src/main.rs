use std::fs::File;
use std::io::prelude::*;
use std::path::Path;

fn main() {
    // Crear un path al archivo de resultados
    let path = Path::new("/home/pablo/academic/institutos_pablo/resultados_finales.csv");
    let display = path.display();
    // Abrir el archivo con modo read-only
    let mut file = match File::open(&path) {
        Err(why) => panic!("no se pudo abrir: {}, {}", display, why),
        Ok(file) => file, 
    }; 
    let mut s = String::new();

    match file.read_to_string(&mut s) {
        Err(why) => panic!("no se pudo leer: {}, {}", display, why),
        Ok(_) => println!("el contenido del archivo {} es: {}", display, s),
    }
}
