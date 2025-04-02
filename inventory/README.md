# FastAPI Inventory Project

This project is a FastAPI application for managing Inventory. It includes endpoints for creating, retrieving, inventory and warehouse.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. Install dependencies using `pipenv`:

    ```sh
    pipenv install
    ```

3. Activate the virtual environment:

    ```sh
    pipenv shell
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory of the project and add the following environment variables:

    ```env
    DB_USER=
    DB_PASSWORD=
    DB_HOST=
    DB_PORT=
    DB_NAME=
    ```

## Running the Application

1. Start the Memcached server using Docker:

    ```sh
    docker run -d --name memcached -p 11211:11211 memcached
    ```

2. Run the FastAPI application:

    ```sh
    uvicorn main:app --port 8000 --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.


## Running Tests

To run the tests, use the following command:

```sh
pytest --cov=. -v -s --cov-fail-under=80
```

Pre commit

```
pre-commit install

<!-- manually -->
pre-commit run --all-files

```

Run black
```
<!-- All files -->
black .
<!-- Single file -->
black path_to_file
```


# Inventory endpoints

## 1. Consulta de salud del servicio

Usado para verificar el estado del servicio.

<table>
<tr>
<td> Método </td>
<td> GET </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/health</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td> N/A </td>
</tr>
<tr>
<td> Encabezados </td>
<td>N/A</td>
</tr>
<tr>
<td> Cuerpo </td>
<td> N/A </td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 200 </td>
<td> Solo para confirmar que el servicio está arriba.</td>
<td>

```pong```
</td>
</tr>
</tbody>
</table>

## 2. Restablecer base de datos

Usado para limpiar la base de datos del servicio.

<table>
<tr>
<td> Método </td>
<td> POST </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/reset</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td> N/A </td>
</tr>
<tr>
<td> Encabezados </td>
<td>N/A</td>
</tr>
<tr>
<td> Cuerpo </td>
<td> N/A </td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 200 </td>
<td> Todos los datos fueron eliminados.</td>
<td>

```
{"msg": "Todos los datos fueron eliminados"}
```
</td>
</tr>
</tbody>
</table>

## 3. Creación de bodegas

Crea una nueva bodega.

<table>
<tr>
<td> Método </td>
<td> POST </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/warehouse</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td> N/A </td>
</tr>
<tr>
<td> Encabezados </td>
<td>

```Authorization: Bearer token```
</td>
</tr>
<tr>
<td> Cuerpo </td>
<td>

```json
{
  "warehouse_name": nombre de la bodega,
  "country": pais en donde está la bodega,
  "city": pais en donde está la bodega,
  "address": direccion de la bodega,
  "phone": telefono de contacto de la bodega
}
```
</td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 401 </td>
<td>El token no es válido o está vencido.</td>
<td> N/A </td>
</tr>
<tr>
<td> 403 </td>
<td>No hay token en la solicitud</td>
<td> N/A </td>
</tr>
<tr>
<td> 400 </td>
<td>En el caso que alguno de los campos no esté presente en la solicitud, o no tengan el formato esperado.</td>
<td> N/A </td>
</tr>
<tr>
<td> 412 </td>
<td>En el caso que los valores de los campos no estén entre lo esperado, por ejemplo el pais o ciudad no existe.</td>
<td> N/A </td>
</tr>
<tr>
<td> 201 </td>
<td>En el caso que la bodega se haya creado con éxito.</td>
<td>

```json
{
  "warehouse_id": id de la bodega,
  "warehouse_name": nombre de la bodega,
  "country": pais en donde está la bodega,
  "city": ciudad en donde está la bodega,
  "address": direccion de la bodega,
  "phone": telefono de contacto de la bodega,
  "created_at": fecha y hora de creación de la bodega en formato ISO
}
```
</td>
</tr>
</tbody>
</table>

## 4. Consultar y filtrar bodegas

Retorna el listado de bodegas que coinciden con los parámetros brindados. Solo un usuario autorizado puede realizar esta operación.

<table>
<tr>
<td> Método </td>
<td> GET </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/warehouse?id={warehouseId}&name={warehouseName}</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td>
Todos los parámetros son opcionales, y su funcionamiento es de tipo AND.
<ol>
<li>id: id de la bodega que se desea consultar.</li>
<li>name: nombre parcial o completo de bodega que se desea consultar.</li>
</ol>
En el caso de que ninguno esté presente se devolverá la lista de datos sin filtrar. Es decir, todas las bodegas disponibles.
</td>
</tr>
<tr>
<td> Encabezados </td>
<td>

```Authorization: Bearer token```
</td>
</tr>
<tr>
<td> Cuerpo </td>
<td> N/A </td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 401 </td>
<td>El token no es válido o está vencido.</td>
<td> N/A </td>
</tr>
<tr>
<td> 403 </td>
<td>No hay token en la solicitud</td>
<td> N/A </td>
</tr>
<tr>
<td> 400 </td>
<td>En el caso que alguno de los campos de búsqueda no tenga el formato esperado.</td>
<td> N/A </td>
</tr>
<tr>
<td> 200 </td>
<td>Listado de bodegas que corresponden a los parametros de búsqueda.</td>
<td>

```json
[
  {
    "warehouse_id": id de la bodega,
    "warehouse_name": nombre de la bodega,
    "country": pais en donde está la bodega,
    "city": pais en donde está la bodega,
    "address": direccion de la bodega,
    "phone": telefono de contacto de la bodega,
    "last_update": fecha de la ultima actualización de los datos de la bodega
  }
]
```
</td>
</tr>
</tbody>
</table>

## 5. Consultar bodega

Retorna el detalle de una bodega, solo un usuario autorizado puede realizar esta operación.

<table>
<tr>
<td> Método </td>
<td> GET </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/warehouse{id}</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td> id: id de la bodega que se desea consultar. </td>
</tr>
<tr>
<td> Encabezados </td>
<td>

```Authorization: Bearer token```
</td>
</tr>
<tr>
<td> Cuerpo </td>
<td> N/A </td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 401 </td>
<td> El token no es válido o está vencido.</td>
<td> N/A </td>
</tr>
<tr>
<td> 403 </td>
<td> No hay token en la solicitud</td>
<td> N/A </td>
</tr>
<tr>
<td> 400 </td>
<td> El id de la bodega no es un valor string con formato uuid.</td>
<td> N/A </td>
</tr>
</tr>
<tr>
<td> 404 </td>
<td> No existe una bodega con ese id.</td>
<td> N/A </td>
</tr>
<tr>
<td> 200 </td>
<td> Detalle de la bodega que corresponde al identificador.</td>
<td>

```json
  {
    "warehouse_id": id de la bodega,
    "warehouse_name": nombre de la bodega,
    "country": pais en donde está la bodega,
    "city": pais en donde está la bodega,
    "address": direccion de la bodega,
    "phone": telefono de contacto de la bodega,
    "last_update": fecha de la ultima actualización de los datos de la bodega
  }
```
</td>
</tr>
</tbody>
</table>

## 6. Carga de inventario

Crea el inventario de un producto si este no existe, en caso contrario actualiza las cantidades del producto.

<table>
<tr>
<td> Método </td>
<td> POST </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/stock</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td> N/A </td>
</tr>
<tr>
<td> Encabezados </td>
<td>

```Authorization: Bearer token```
</td>
</tr>
<tr>
<td> Cuerpo </td>
<td>

```json
[
  {
    "product_id":id del producto,
    "warehouse_id": id de la bodega,
    "quantity": unidades del producto que se desean registrar en la bodega,
  }
]
```
</td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 401 </td>
<td>El token no es válido o está vencido.</td>
<td> N/A </td>
</tr>
<tr>
<td> 403 </td>
<td>No hay token en la solicitud</td>
<td> N/A </td>
</tr>
<tr>
<td> 400 </td>
<td>En el caso que alguno de los campos no esté presente en la solicitud, o no tengan el formato esperado.</td>
<td> N/A </td>
</tr>
<tr>
<td> 412 </td>
<td>En el caso que los valores de los campos no estén entre lo esperado, por ejemplo la bodega no existe o las cantidades son negativas.</td>
<td> N/A </td>
</tr>
<tr>
<td> 201 </td>
<td>En el caso que la carga de inventario se haya realizado con éxito.</td>
<td>

```json
{
  "operation_id": id de la operación de carga,
  "user_id": id del usuario que realizó la carga de inventario,
  "created_at": fecha y hora en que se realizó la carga de inventario, en formato ISO
}
```
</td>
</tr>
</tbody>
</table>

## 7. Ver y filtrar el inventario

Retorna el listado de inventario que coinciden con los parámetros brindados. Solo un usuario autorizado puede realizar esta operación.

<table>
<tr>
<td> Método </td>
<td> GET </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/stock?product={productId}&warehouse={warehouseId}</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td>
Todos los parámetros son opcionales, y su funcionamiento es de tipo AND.
<ol>
<li>product: id del producto que se desea consultar.</li>
<li>warehouse: id de la bodega que se desea consultar.</li>
</ol>
En el caso de que ninguno esté presente se devolverá la lista de datos sin filtrar. Es decir, todo el inventario disponible.
</td>
</tr>
<tr>
<td> Encabezados </td>
<td>

```Authorization: Bearer token```
</td>
</tr>
<tr>
<td> Cuerpo </td>
<td> N/A </td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 401 </td>
<td>El token no es válido o está vencido.</td>
<td> N/A </td>
</tr>
<tr>
<td> 403 </td>
<td>No hay token en la solicitud</td>
<td> N/A </td>
</tr>
<tr>
<td> 400 </td>
<td>En el caso que alguno de los campos de búsqueda no tenga el formato esperado.</td>
<td> N/A </td>
</tr>
<tr>
<td> 200 </td>
<td>Listado de inventario que corresponden a los parametros de búsqueda.</td>
<td>

```json
[
  {
    "product_id":id del producto,
    "warehouse_id": id de la bodega,
    "quantity": unidades disponibles del producto en la bodega,
    "last_update": fecha de la ultima actualización del inventario
  }
]
```
</td>
</tr>
</tbody>
</table>

## 8. Consultar inventario de un producto

Retorna el inventario de un producto, solo un usuario autorizado puede realizar esta operación.

<table>
<tr>
<td> Método </td>
<td> GET </td>
</tr>
<tr>
<td> Ruta </td>
<td> <strong>/inventory/stock/{id}</strong> </td>
</tr>
<tr>
<td> Parámetros </td>
<td> id: id del producto que se desea consultar. </td>
</tr>
<tr>
<td> Encabezados </td>
<td>

```Authorization: Bearer token```
</td>
</tr>
<tr>
<td> Cuerpo </td>
<td> N/A </td>
</tr>
</table>

### Respuestas

<table>
<tr>
<th> Código </th>
<th> Descripción </th>
<th> Cuerpo </th>
</tr>
<tbody>
<tr>
<td> 401 </td>
<td>El token no es válido o está vencido.</td>
<td> N/A </td>
</tr>
<tr>
<td> 403 </td>
<td>No hay token en la solicitud</td>
<td> N/A </td>
</tr>
<tr>
<td> 400 </td>
<td>El productId no es un valor string con formato uuid.</td>
<td> N/A </td>
</tr>
</tr>
<tr>
<td> 404 </td>
<td> No existe inventario para el producto con ese id.</td>
<td> N/A </td>
</tr>
<tr>
<td> 200 </td>
<td>Inventario del producto que corresponde al identificador.</td>
<td>

```json
  {
    "product_id":id del producto,
    "warehouse_id": id de la bodega,
    "quantity": unidades disponibles del producto en la bodega,
    "last_update": fecha de la ultima actualización del inventario
  }
```
</td>
</tr>
</tbody>
</table>

### 9. Consulta del inventario en tiempo real


Establece una conexión WebSocket para recibir actualizaciones del inventario en tiempo real. Solo un usuario autorizado puede establecer esta conexión.

<table> 
<tr> 
<td> Protocolo </td> 
<td> WebSocket </td> 
</tr> 
<tr> 
<td> Evento </td> 
<td> <strong>inventory_updates</strong> </td> 
</tr> 
<tr> 
<td> Opciones del socket </td> 
<td> auth.token: token de autenticación en formato JWT</td>
</td> 
</tr> 
<tr>
<td> Cuerpo (opcional) </td>
<td>

```json
  {
    "product_id":id del producto,
    "warehouse_id": id de la bodega
  }
```
</td>
</tr>
</table>



### Respuestas
<table> 
<tr> 
<th> Evento </th> 
<th> Descripción </th> 
<th> Formato del mensaje </th> 
</tr> 
<tbody> 
<tr> 
<td> updated </td> 
<td>Se recibe cuando hay una actualización en el inventario que coincide con los filtros establecidos.</td> 
<td>

```json
{
  "product_id": id del producto,
  "warehouse_id": id de la bodega,
  "quantity": nueva cantidad disponible,
  "last_update": fecha y hora de la actualización en formato ISO
}
```
</td> 
</tr> 
<tr> 
<td> created </td> 
<td>Se recibe cuando se crea un nuevo registro de inventario que coincide con los filtros establecidos.</td> 
<td>

```json
{
  "product_id": id del producto,
  "warehouse_id": id de la bodega,
  "quantity": cantidad inicial del producto,
  "last_update": fecha y hora de la creación en formato ISO
}
```
</td> </tr> <tr> <td> error </td> <td>Se recibe cuando ocurre un error en la conexión WebSocket.</td> <td>

```json
{
  "code": código del error,
  "message": descripción del error
}
```
</td> 
</tr> 
</tbody> 
</table>
