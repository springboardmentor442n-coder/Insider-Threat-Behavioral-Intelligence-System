import api from "./api";

export async function loginUser(username,password){

    const formData = new URLSearchParams();

    formData.append("username",username);

    formData.append("password",password);

    const response = await api.post(

        "/auth/login",

        formData,

        {

            headers:{

                "Content-Type":"application/x-www-form-urlencoded"

            }

        }

    );

    return response.data;

}
