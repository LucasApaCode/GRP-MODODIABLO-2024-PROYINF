<?php include('../templates/header.php'); ?>    
    
  <div class="container py-5 h-100" data-aos="fade-up" data-aos-duration="1000">
    <div class="row d-flex justify-content-center align-items-center h-100">
      <div class="col col-xl-10">
        <div class="card" style="border-radius: 1rem;">
          <div class="row g-0">
            <div class="col-md-6 col-lg-5 d-none d-md-block">
              <img src="../img/doctor.png"
                alt="login form" class="img-fluid" style="border-radius: 1rem 0 0 1rem;" />
            </div>
            <div class="col-md-6 col-lg-7 d-flex align-items-center">
              <div class="card-body p-4 p-lg-5 text-black">

              <form action="index.php" method="post">

                    <div class="d-flex align-items-center mb-3 pb-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-person-raised-hand" viewBox="0 0 16 16">
                    <path d="M6 6.207v9.043a.75.75 0 0 0 1.5 0V10.5a.5.5 0 0 1 1 0v4.75a.75.75 0 0 0 1.5 0v-8.5a.25.25 0 1 1 .5 0v2.5a.75.75 0 0 0 1.5 0V6.5a3 3 0 0 0-3-3H6.236a1 1 0 0 1-.447-.106l-.33-.165A.83.83 0 0 1 5 2.488V.75a.75.75 0 0 0-1.5 0v2.083c0 .715.404 1.37 1.044 1.689L5.5 5c.32.32.5.754.5 1.207"/>
                    <path d="M8 3a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3"/>
                    </svg>
                    <i class="fas fa-cubes fa-2x me-3" style="color: #ff6219;"></i>
                    <span class="h1 fw-bold mb-0">¡Bienvenido/a!</span>
                  </div>

                  <h5 class="fw-normal mb-3 pb-3" style="letter-spacing: 1px;">Ingresa a tu cuenta</h5>

                  <div data-mdb-input-init class="form-outline mb-4">
                    <input type="number" id="form2Example17" class="form-control form-control-lg" />
                    <label class="form-label" for="form2Example17">RUT o DNI</label>
                  </div>

                  <div data-mdb-input-init class="form-outline mb-4">
                    <input type="password" id="form2Example27" class="form-control form-control-lg" />
                    <label class="form-label" for="form2Example27">Contraseña</label>
                  </div>

                  <div class="pt-1 mb-4">
                    <button data-mdb-button-init data-mdb-ripple-init class="btn btn-dark btn-lg btn-block" type="submit">Ingresar</button>
                  </div>

                  <a class="small text-muted" href="forget.php">¿Olvidaste tu contraseña?</a>
                  <p class="mb-5 pb-lg-2" style="color: #393f81;">¿No tienes cuenta? <a href="signup.php"
                      style="color: #393f81;">Registrate aquí</a><br>
                  ¿Eres paciente? <a href="login_paciente.php"
                      style="color: #393f81;">Ingresa aquí</a></p>
                </form>

              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<?php include('../templates/footer.php'); ?>