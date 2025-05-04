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
  {
    "product_id":id del producto,
    "warehouse_id": id de la bodega,
    "quantity": unidades del producto que se desean registrar en la bodega,
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
  "warehouse_id": id de la bodega en donde se realizó la carga de inventario,
  "processed_records": número de registros procesados,
  "successful_records": número de registros cargados exitosamente,
  "failed_records": número de registros que fallaron,
  "created_at": fecha y hora en que se realizó la carga de inventario, en formato ISO
}
```
</td>
</tr>
</tbody>
</table>


## 7. Bulk Upload Inventory from CSV
### `POST /inventory/stock/csv`

Uploads multiple inventory records via CSV file.

---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---
📥 Request
Multipart form with:

- `warehouse_id`: ID of the warehouse
- `inventory-upload`: CSV file with columns:
  - `product_id`: ID of the product
  - `quantity`: Units of product to register

---

📤 Response (201 Created)

```json
{
  "operation_id": id de la operación de carga,
  "warehouse_id": id de la bodega en donde se realizó la carga de inventario,
  "processed_records": número de registros procesados,
  "successful_records": número de registros cargados exitosamente,
  "failed_records": número de registros que fallaron,
  "created_at": fecha y hora en que se realizó la carga de inventario, en formato ISO
}
```

❌ Error Responses

401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```
400 Bad Request
```json
{
  "detail": "Invalid CSV file or missing required columns"
}
```
412 Precondition Failed
```json
{
  "detail": "Invalid field values"
}
```

## 8. View and Filter Inventory
### `GET /inventory/stock?product={productId}&warehouse={warehouseId}`

Retrieves inventory records filtered by optional parameters.

---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---
📝 Query Parameters

| Parameter | Type | Required	| Description |
|-|-|-|-|
|product|string|❌|Filter by product ID|
|warehouse|string|❌|Filter by warehouse ID|

---
📤 Response (200 OK)

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

❌ Error Responses

401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```
400 Bad Request
```json
{
  "detail": "Invalid search parameters"
}
```

## 9. Get consolidated inventory catalog
### `GET /inventory/stock/catalog/`

Retrieves detailed information about a products catalog available on CCP.
---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---

📤 Response (200 OK)

```json
[{
    "product_id": Id del producto en formato UUID,
    "product_name": Nombre del producto,
    "product_code": Codigo del producto,
    "manufacturer_name": Nombre del fabricante,
    "price": Precio unitario del producto,
    "images": ["https://example.com/images1.jpg", "https://example.com/images2.jpg"],
    "quantity": Cantidad del producto disponible en el inventario 
}]
```

❌ Error Responses

401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```

## 10. Consulta del inventario en tiempo real
### `WebSocket /inventory/stock/ws/`

Establishes a WebSocket connection for real-time inventory updates.
---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---

📤 Response

```json
{
  "product_id": "string",
  "quantity": "number",
  "last_update": "string"
}
```


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
