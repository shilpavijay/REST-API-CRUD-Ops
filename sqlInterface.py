from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions
from sqlalchemy import create_engine,Table, MetaData, Column, Integer, String, ForeignKey, Sequence, select
from sqlalchemy.orm import sessionmaker

app = FlaskAPI(__name__)

engine = create_engine('mysql://root:python098@localhost/gotest', echo=True)
conn = engine.connect()
Session = sessionmaker(bind=engine)

session = Session()
metadata = MetaData(bind=None)

@app.route("/CreateTable", methods=['GET'])
def create_table():
	Employee = Table('Employee', metadata,
				Column('ID', Integer, Sequence('user_id_seq'), primary_key=True),
				Column('Name', String(50)),
				Column('Age', Integer),
				Column('Sal', Integer),
				Column('Dept', String(50))
					)

	metadata.create_all(engine)
	response = {"msg": "Table 'Employee' created"}
	return response


@app.route("/", methods=['GET','POST','PUT'])
def list_table_data():
	Employee = Table('Employee', metadata, autoload = True, autoload_with = engine)
	stmt = select([Employee])
	result = conn.execute(stmt)

	if request.method == 'GET':
		response = {row.ID:{'ID':row.ID,'Name':row.Name, 'Age':row.Age, 'Sal':row.Sal, 'Dept':row.Dept} for row in result}
		return response

	if request.method in ['POST','PUT']:
		Name = str(request.data.get('Name',''))
		Age = int(request.data.get('Age',0))
		Sal = int(request.data.get('Sal',0))
		Dept = str(request.data.get('Dept',''))
		if request.method == 'POST':
			ID = int(max([r.ID for r in result]))+1
			stmt = Employee.insert().\
			    values(ID=ID,Name=Name,Age=Age,Sal=Sal,Dept=Dept)
			conn.execute(stmt)
			return '', status.HTTP_201_CREATED

		else:
			print(request.data)
			ID = int(request.data.get('ID',''))
			stmt = Employee.update().where(Employee.c.ID == ID).values(Name=Name,Age=Age,Sal=Sal,Dept=Dept)
			conn.execute(stmt)
			return '',status.HTTP_202_ACCEPTED

@app.route("/<int:id>/", methods=['GET', 'DELETE'])
def delete_data(id):
	Employee = Table('Employee', metadata, autoload = True, autoload_with = engine)
	stmt = select([Employee]).where(Employee.c.ID == int(id))
	result = conn.execute(stmt)

	if request.method == 'DELETE':
		stmt = Employee.delete().where(Employee.c.ID == int(id))
		conn.execute(stmt)
		return '', status.HTTP_204_NO_CONTENT

	response = {row.ID:[row.Name, row.Age, row.Sal, row.Dept] for row in result}
	response.update({'url': request.host_url.rstrip('/')})
	return response

if __name__ == "__main__":
    app.run(debug=True)
