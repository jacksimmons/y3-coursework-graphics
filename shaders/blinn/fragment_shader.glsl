# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
in vec3 position_view_space;   // the position in view coordinates of this fragment

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec3 final_color;

// === uniform here the texture object to sample from
uniform int mode;	// the rendering mode (better to code different shaders!)

// material uniforms
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

// light source
uniform vec3 light;
uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;

///=== main shader code
void main() {
      // 1. calculate vectors used for shading calculations
      vec3 camera_direction = -normalize(position_view_space);
      vec3 light_direction = normalize(light-position_view_space);

      // 2. Calculate the normal to the fragment using position of its neighbours
      vec3 xTangent = dFdx( position_view_space );
      vec3 yTangent = dFdy( position_view_space );
      vec3 normal_view_space = normalize( cross( xTangent, yTangent ) );

      // 3. now we calculate light components
      vec3 ambient = Ia*Ka;
      vec3 diffuse = Id*Kd*max(0.0f,dot(light_direction, normal_view_space));
      vec3 specular = Is*Ks*pow(max(0.0f, dot(reflect(light_direction, normal_view_space), -camera_direction)), Ns);

      // 4. we calculate the attenuation function
      // in this formula, dist should be the distance between the surface and the light
      float dist = length(light - position_view_space);
      float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

      // 5. Finally, we combine the shading components
      final_color = ambient + attenuation*(diffuse + specular);
}


