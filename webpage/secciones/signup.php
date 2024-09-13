<?php include('../templates/header.php'); ?>   

<section class="vh-100 gradient-custom">
  <div class="container py-5 h-100" data-aos="fade-up" data-aos-duration="700">
    <div class="row justify-content-center align-items-center h-100">
      <div class="col-12 col-lg-9 col-xl-7">
        <div class="card shadow-2-strong card-registration" style="border-radius: 15px;">
          <div class="card-body p-4 p-md-5">
            <h3 class="mb-4 pb-2 pb-md-0 mb-md-5">Cree su cuenta</h3>
            <form>

              <div class="row">
                <div class="col-md-6 mb-4">

                  <div data-mdb-input-init class="form-outline">
                    <input type="text" id="nombre" class="form-control form-control-lg" />
                    <label class="form-label" for="nombre">Nombre</label>
                  </div>

                </div>
                <div class="col-md-6 mb-4">

                  <div data-mdb-input-init class="form-outline">
                    <input type="text" id="apellido" class="form-control form-control-lg" />
                    <label class="form-label" for="apellido">Apellido</label>
                  </div>

                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-4 pb-2">

                  <div data-mdb-input-init class="form-outline">
                    <input type="number" id="rut" class="form-control form-control-lg" />
                    <label class="form-label" for="rut">RUT o DNI</label>
                  </div>

                </div>
                <div class="col-md-6 mb-4 pb-2">

                  <div data-mdb-input-init class="form-outline">
                    <input type="password" id="contrasena" class="form-control form-control-lg" />
                    <label class="form-label" for="contrasena">Contraseña</label>
                  </div>

                </div>
              </div>

            <div class>
              <div class="col-lg-6 col-sm-6">
                        <label for="startDate">Fecha de nacimiento</label>
                        <input id="startDate" class="form-control" type="date" />
                        <span id="startDateSelected"></span>
                </div>
            </div><br>

            <div class="row">
                
                <div class="col-md-12 mb-4">

                  <h6 class="mb-2 pb-1">Género: </h6>

                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="inlineRadioOptions" id="femaleGender"
                      value="option1" checked />
                    <label class="form-check-label" for="femaleGender">Femenino</label>
                  </div>

                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="inlineRadioOptions" id="maleGender"
                      value="option2" />
                    <label class="form-check-label" for="maleGender">Masculino</label>
                  </div>

                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="inlineRadioOptions" id="otherGender"
                      value="option3" />
                    <label class="form-check-label" for="otherGender">Otro</label>
                  </div>

                </div>
              </div>

              <div class="mt-4 pt-2">
                <input data-mdb-ripple-init class="btn btn-primary btn-lg" type="submit" value="Registrarme" />
              </div>

            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<?php include('../templates/footer.php'); ?>