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

// Texture Sampler
uniform sampler2D texture_object; // first texture object

// Material properties
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

// Texture scaling in blender
uniform vec3 tex_scale;

// light source
uniform vec3 light_pos;
uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;

uniform float alpha;
uniform int blinn;


///=== main shader code
void main() {    
    vec4 texval = vec4(1.0f);
    if(has_texture == 1)
        texval = texture2D(texture_object, fragment_tex_coord * tex_scale.xy);
    
    vec3 normal = normalize(fragment_normal);
    vec3 light_dir = normalize(light_pos - fragment_pos);
    vec3 camera_dir = -normalize(fragment_pos);

    // === Ambient Reflection
    vec4 ambient = vec4(Ka * Ia, alpha);
    
    // === Diffuse Reflection
    // A . B = |A||B|cos(theta)
    // |normal| and |light_dir| are 1
    // => diff = cos(theta)
    // If the angle > 90 deg, then dot product becomes negative.
    // max function ensures negative lighting does not occur (which is undefined).
    float angle_normal_light = max(dot(normal, light_dir), 0.0f);
    vec4 diffuse = vec4(Kd * Id, alpha) * angle_normal_light;

    // === Specular Reflection
    // Need to negate light_dir, as it points toward the light.
    // The `reflect` function expects a vector pointing out from
    // the light source. It is then reflected over the normal.
    
    float spec = 0.0f;
    if (blinn == 0)
    {
        // Phong
        vec3 reflect_dir = reflect(-light_dir, normal);
        spec = pow(max(dot(camera_dir, reflect_dir), 0.0f), Ns);
    }
    else
    {
        // Blinn-Phong
        vec3 halfway_dir = normalize(light_dir + camera_dir);
        spec = pow(max(dot(fragment_normal, halfway_dir), 0.0f), Ns);
    }
    vec4 specular = vec4(Is * Ks * spec, alpha);
    
    // Overwrite specular component if exponent is 0
    if (Ns == 0) {
        specular = vec4(0.0f);
    }

    final_color = (ambient + diffuse) * texval + specular;
}


