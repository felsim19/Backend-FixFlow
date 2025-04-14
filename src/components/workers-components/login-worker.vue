const loginWorker = async () => {
    try {
        if (selectedPremise.value || workersCount.value === 1) {
            const answer = await axios.post(`/api/loginWorker/${loggedCompany.value}`, {
                document: sessionworker.value.document,
                password: sessionworker.value.password,
            });
            
            // Guardar datos del trabajador
            loggedDocument.value = answer.data.id;
            localStorage.setItem("loggedDocument", JSON.stringify(answer.data.id));
            msg.value = answer.data.status;
            loggedWorker.value = answer.data.wname;
            localStorage.setItem("loggedWorker", JSON.stringify(answer.data.wname));
            workerRole.value = answer.data.role;
            localStorage.setItem("workerRole", JSON.stringify(answer.data.role));
            
            // Si es el primer gerente, redirigir a crear local
            if (answer.data.is_first_manager) {
                router.push('/premises/new-premise');
                return;
            }
            
            // Solo guardar startShift si hay un local seleccionado y no es el primer gerente
            if (selectedPremise.value) {
                startShift.value = answer.data.shift;
                localStorage.setItem("startShift", JSON.stringify(answer.data.shift));
                router.push('/bills');
            } else {
                showAlert("2", "Necesitas iniciar en un local para empezar un turno");
            }
        } else {
            showAlert("2", "Necesitas iniciar en un local para empezar un turno");
        }

    } catch (error) {
        if (error.response && error.response.data) {
            showAlert("2", `Error al iniciar sesión: ${error.response.data.detail}`);
            console.error("Error al iniciar sesión", error.response.data);
        } else {
            showAlert("2", "Ha ocurrido un error inesperado. Inténtalo de nuevo.");
            console.error(error);
        }
    }
} 