<script setup lang="ts">
const secret = ref(false)
let buffer = ''

function onKeydown(e: KeyboardEvent) {
  buffer += e.key.toLowerCase()
  buffer = buffer.slice(-3)
  if (buffer === 'sad') secret.value = true
}
</script>

<template>
<div class="lcont">
  <div class="vcont">
    <h1>New Plush</h1>
    <form ref="registerForm" autocomplete="off" data-1p-ignore data-bwignore data-lpignore="true" data-form-type="other" @keydown="onKeydown">
      <div class="field">
        <input
          id="name"
          name="name"
          type="text"
          placeholder=" "
          minlength="3"
          maxlength="96"
          pattern="(?:[A-Za-z0-9_]|-){3,96}"
          required
        />
        <label for="name">Name *</label>
      </div>

      <div class="half">
        <div class="field">
          <input
            id="date"
            name="date"
            type="date"
            required
          />
          <label for="date">Date of Adoption *</label>
        </div>

        <div class="field">
          <input
            id="size"
            name="size"
            placeholder="55cm or 100cm"
            type="number"

            required
          />
          <label for="size">Size *</label>
          <span class="unit">cm</span>
        </div>
      </div>

      <div class="field">
        <textarea
          id="description"
          name="description"
          rows="3"
          placeholder=" "
          required
        />
        <label for="description">Description *</label>
      </div>

      <div class="field">
        <input
          id="location"
          name="location"
          placeholder="IKEA San Francisco"
          type="text"
        />
        <label for="location">Location</label>
      </div>

      <div class="half">
        <div class="field">
          <input
            id="gender"
            name="gender"
            type="text"
          />
          <label for="location">Gender</label>
        </div>
        <div class="field">
          <input
            id="pronouns"
            name="pronouns"
            type="text"
          />
          <label for="location">Pronouns</label>
        </div>
      </div>

      <div class="field">
        <input
          id="lastwashed"
          name="lastwashed"
          type="datetime-local"
          placeholder=""
       />
        <label for="lastwashed">Last wash</label>
      </div>

      <div class="half">
        <div class="field">
          <input
            id="floof"
            name="floof"
            placeholder="1 to 10"
            type="number"
            min="1"
            max="10"
          />
          <label for="floof">Fluffiness rating</label>
        </div>

        <div class="field">
          <input
            id="squish"
            name="squish"
            placeholder="1 to 10"
            type="number"
            min="1"
            max="10"
          />
          <label for="squish">Squishiness</label>
        </div>
      </div>

      <div class="field" v-if="secret">
        <input
          id="mloftearsabsorbed"
          name="mloftearsabsorbed"
          type="number"
        />
        <label for="mloftearsabsorbed">mL of tears absorbed</label>
      </div>
      <button type="submit">Submit</button>
    </form>
  </div>
</div>
</template>

<style>
html, body {
  height: 100%;
  margin: 0;
}

body {
  overflow: hidden;
  font-family: "Noto Sans";
}

#app, #__nuxt {
  height: 100%;
}

.lcont, .vcont {
  box-sizing: border-box;
}

.lcont {
  width: 50vw;
  height: 100svh;
  position: relative;
  float: left;
  padding: 1em;
  overflow: hidden;
}

.vcont {
  padding: 1em;
  height: 100%;
  width: 100%;
  background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

h1 {
  margin: 0.25em;
}

input,
textarea {
  border-radius: 1rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 600;
  color: black;
}

form {
  display: flex;
  flex-direction: column;
  margin-top: 1.5rem;
  gap: 1rem;
  height: 100%;
  width: 100%;
}

.field {
  position: relative;
}

.field input,
.field textarea{
  height: 3rem;
  width: 100%;
  padding: 1rem 0.75rem 0.25rem 0.9rem;
  box-sizing: border-box;
}

.field input[type="number"] {
  -moz-appearance: textfield;
}

.field input[type="number"]::-webkit-outer-spin-button,
.field input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.field .unit {
  position: absolute;
  right: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: #3A4A5A;
  font-weight: 600;
  pointer-events: none;
}

.field label {
  position: absolute;
  left: 1.1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  font-weight: 500;
  color: #4A5A6A;
  pointer-events: none;
  transition: all 0.15s ease-out;
}

.field input:focus + label,
.field input:not(:placeholder-shown) + label,
.field textarea:focus + label,
.field textarea:not(:placeholder-shown) + label{
  top: 0.7rem;
  font-size: 0.7rem;
  color: #2A3A4A;
  font-weight: 700;
}

form input {
  max-width: 100%;
}

form button {
  margin-top: 0.5em;
  width: 100%;
  height: 2.5rem;
}

button {
  border-radius: 1rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 700;
}

button:hover {
  border: 3px solid #95ADB6;
  background-color: #E3F0F5;
}

button:active {
  border: 3px solid #859DA6;
  background-color: #A3B0B5;
}

input:user-invalid,
textarea:user-invalid {
  border: 2px solid #EF959C;
  background-color: #F7CACE;
}

.half {
  display: flex;
  gap: 1rem;
}

.half .field {
  flex: 1;
}

#description {
  height: 4.5rem;
  resize: none;
}
</style>
