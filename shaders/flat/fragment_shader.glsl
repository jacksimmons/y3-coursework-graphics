#version 330 core

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_normal;
in vec3 fragment_pos; // View coordinates position of this fragment
in vec2 fragment_tex_coord;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;

// === uniform here the texture object to sample from
uniform int mode;	// the rendering mode (better to code different shaders!)

uniform int has_texture;

// texture samplers
uniform sampler2D textureObject; // first texture object

// material uniforms
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

// light source
uniform vec3 light_pos;
uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;

///=== main shader code
void main() {    
    vec4 texval = vec4(1.0f);
    if(has_texture == 1)
        texval = texture2D(textureObject, fragment_tex_coord);
    vec3 normal = normalize(fragment_normal);
    vec3 light_dir = normalize(light_pos - fragment_pos);
    vec3 camera_dir = -normalize(fragment_pos);

    // === Ambient Reflection
    vec4 ambient = vec4(Ka * Ia, 1.0f);
    
    // === Diffuse Reflection
    // A . B = |A||B|cos(theta)
    // |normal| and |light_dir| are 1
    // => diff = cos(theta)
    // If the angle > 90 deg, then dot product becomes negative.
    // max function ensures negative lighting does not occur (which is undefined).
    float angle_normal_light = max(dot(normal, light_dir), 0.0f);
    vec4 diffuse = vec4(Kd * Id, 1.0f) * angle_normal_light;

    // === Specular Reflection
    // Need to negate light_dir, as it points toward the light.
    // The `reflect` function expects a vector pointing out from
    // the light source. It is then reflected over the normal.
    vec3 reflect_dir = reflect(-light_dir, normal);
    float angle_reflection_camera = max(dot(camera_dir, reflect_dir), 0.0f);
    vec4 specular = vec4(Is * Ks * pow(angle_reflection_camera, Ns), 1.0f);

    final_color = (ambient + diffuse) * texval + specular;
}


